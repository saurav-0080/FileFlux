"""
Undo system for FileFlux.

Restores files moved during the last organization session
using records stored in the SQLite database.
"""

import shutil
from pathlib import Path
from app import database, history
from app.logger import setup_logger

logger = setup_logger()


class UndoManager:
    """Restores files from the last organization session."""

    def __init__(self, conn):
        self.conn = conn

    def undo_last_session(self) -> dict:
        """
        Undo all file moves from the most recent session.

        Returns:
            Summary dict with restored, skipped, and failed counts.
        """
        session_id = history.get_last_session(self.conn)
        if not session_id:
            logger.info("No session found to undo")
            return {"restored": 0, "skipped": 0, "failed": 0}

        logger.info(f"Undo started for session: {session_id}")
        records = history.get_history(self.conn, session_id)

        restored = 0
        skipped = 0
        failed = 0

        for record in records:
            result = self.undo_file(record)
            if result == "restored":
                restored += 1
            elif result == "skipped":
                skipped += 1
            else:
                failed += 1

        logger.info(f"Undo complete. Restored: {restored}, Skipped: {skipped}, Failed: {failed}")
        return {"restored": restored, "skipped": skipped, "failed": failed}

    def undo_file(self, record) -> str:
        """
        Restore a single file to its original location.

        Returns:
            'restored', 'skipped', or 'failed'
        """
        destination = Path(record["destination_path"])
        original = Path(record["original_path"])

        if not destination.exists():
            logger.warning(f"File no longer exists at destination: {destination}")
            return "skipped"

        result = self.restore_file(destination, original)
        if result:
            self.mark_as_undone(record["id"])
            return "restored"
        return "failed"

    def restore_file(self, source: Path, original: Path) -> bool:
        """
        Move a file back to its original location safely.

        Returns:
            True if successful, False otherwise.
        """
        try:
            original.parent.mkdir(parents=True, exist_ok=True)

            target = original
            if target.exists():
                stem = original.stem
                suffix = original.suffix
                counter = 1
                target = original.parent / f"{stem}_restored{suffix}"
                while target.exists():
                    target = original.parent / f"{stem}_restored({counter}){suffix}"
                    counter += 1

            shutil.move(str(source), str(target))
            logger.info(f"Restored: {source.name} -> {target}")
            return True

        except (PermissionError, OSError) as e:
            logger.warning(f"Failed to restore {source.name}: {e}")
            return False

    def mark_as_undone(self, record_id: int) -> None:
        """Mark a database record as undone."""
        database.execute(self.conn, """
            UPDATE file_history SET undone = 1 WHERE id = ?
        """, (record_id,))