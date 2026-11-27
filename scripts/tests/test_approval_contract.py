"""Shared executable authorization cases for Book release flow contract v1.

Run unchanged in each book. Only the entry-point adapter differs by repository
layout; every input and expected decision below is identical.
"""
import importlib.util
import os
from pathlib import Path
import sys
import unittest


OWNER = "webmaxru"
HEAD = "a" * 40
OLD = "b" * 40


def stamp(second):
    return f"2026-01-01T00:00:{second:02d}Z"


def review(state, second, login=OWNER, head=HEAD):
    return {
        "id": second, "user": {"login": login}, "state": state,
        "submitted_at": stamp(second), "commit_id": head,
    }


def comment(second, body=None, login=OWNER):
    return {
        "id": second, "user": {"login": login},
        "body": f"/release-book {HEAD}" if body is None else body,
        "created_at": stamp(second), "updated_at": stamp(second),
    }


def load_approval():
    root = os.environ.get("BOOK_REPO_ROOT")
    if root:
        root = Path(root).resolve()
    else:
        root = next(
            p for p in Path(__file__).resolve().parents
            if (p / ".github" / "workflows").is_dir()
        )
    entries = (
        ("scripts/approved_book.py", "approved"),
        ("scripts/book_release.py", "approval"),
        ("tools/book_release.py", None),
    )
    for relative, function in entries:
        path = root.joinpath(*relative.split("/"))
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("approval_contract_target", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        if function is None:
            function = "approved" if hasattr(module, "approved") else "approval"
        return getattr(module, function)
    raise RuntimeError(f"No book approval entry point found under {root}")


class ApprovalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decide = staticmethod(load_approval())

    def check(self, expected, author, reviews=(), comments=(), timeline=(), head=HEAD):
        pr = {"user": {"login": author}, "head": {"sha": head}}
        self.assertEqual(bool(self.decide(pr, list(reviews), list(comments), list(timeline))), expected)

    def test_only_owner_authorizes_using_the_correct_channel(self):
        self.check(False, OWNER)
        self.check(False, "contributor")
        self.check(True, OWNER, comments=[comment(2)])
        self.check(True, "contributor", reviews=[review("APPROVED", 2)])
        self.check(False, OWNER, comments=[comment(2, login="outsider")])
        self.check(False, "contributor", reviews=[review("APPROVED", 2, "outsider")])
        self.check(False, "contributor", comments=[comment(2)])
        self.check(False, OWNER, reviews=[review("APPROVED", 2)])

    def test_ordinary_reviews_neither_authorize_nor_revoke(self):
        ordinary = review("COMMENTED", 3)
        self.check(False, "contributor", reviews=[ordinary])
        self.check(True, "contributor", reviews=[review("APPROVED", 2), ordinary])
        self.check(True, OWNER, reviews=[ordinary], comments=[comment(2)])

    def test_push_invalidates_old_head_authorization(self):
        self.check(False, OWNER, comments=[comment(2)], head=OLD)
        self.check(False, "contributor", reviews=[review("APPROVED", 2)], head=OLD)

    def test_command_requires_exact_unedited_whole_body(self):
        exact = f"/release-book {HEAD}"
        for body in (" " + exact, exact + " ", exact + "\n", exact + "\r\n",
                     f"/release-book  {HEAD}", f"/release-book\t{HEAD}",
                     f"/release-book {HEAD.upper()}", f"/release-book {HEAD[:7]}"):
            with self.subTest(body=repr(body)):
                self.check(False, OWNER, comments=[comment(2, body)])
        edited = dict(comment(2), updated_at=stamp(3))
        self.check(False, OWNER, comments=[edited])

    def test_other_comments_do_not_cancel_a_surviving_valid_command(self):
        others = [
            comment(3, "Thanks"), comment(4, f"/release-book {OLD}"),
            comment(5, "/release-book malformed"),
            dict(comment(6), updated_at=stamp(7)),
        ]
        self.check(True, OWNER, comments=[comment(2), *others])
        self.check(False, OWNER, comments=others)

    def test_any_reviewer_change_request_requires_fresh_owner_authorization(self):
        for author in (OWNER, "contributor"):
            for reviewer in (OWNER, "outsider"):
                with self.subTest(author=author, reviewer=reviewer):
                    initial = [] if author == OWNER else [review("APPROVED", 2)]
                    comments = [comment(2)] if author == OWNER else []
                    blocked = initial + [review("CHANGES_REQUESTED", 3, reviewer)]
                    self.check(False, author, blocked, comments)
                    renewed = blocked if author == OWNER else blocked + [review("APPROVED", 4)]
                    fresh = comments + [comment(4)] if author == OWNER else comments
                    self.check(True, author, renewed, fresh)

    def test_any_review_dismissal_uses_the_dismissal_event_time(self):
        for author in (OWNER, "contributor"):
            for reviewer in (OWNER, "outsider"):
                with self.subTest(author=author, reviewer=reviewer):
                    dismissed = review("DISMISSED", 1, reviewer)
                    initial = [dismissed]
                    if author != OWNER:
                        initial.append(review("APPROVED", 2))
                    comments = [comment(2)] if author == OWNER else []
                    self.check(True, author, initial, comments)
                    timeline = [{
                        "event": "review_dismissed", "created_at": stamp(3),
                        "dismissed_review": {"review_id": 1},
                    }]
                    self.check(False, author, initial, comments, timeline)
                    renewed = initial if author == OWNER else initial + [review("APPROVED", 4)]
                    fresh = comments + [comment(4)] if author == OWNER else comments
                    self.check(True, author, renewed, fresh, timeline)

    def test_latest_formal_owner_review_and_strict_barrier_order(self):
        self.check(False, "contributor",
                   [review("APPROVED", 2), review("APPROVED", 3, head=OLD)])
        self.check(False, "contributor",
                   [review("APPROVED", 3), review("CHANGES_REQUESTED", 3, "outsider")])
        self.check(False, OWNER, [review("CHANGES_REQUESTED", 3, "outsider")],
                   [comment(3)])


if __name__ == "__main__":
    unittest.main()
