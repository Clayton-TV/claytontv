from django.core.management.base import BaseCommand, CommandError

from catalogue import search
from catalogue.topic_reconciliation import ReconciliationBlockedError, apply_plan, build_plan, describe_plan

SEARCH_REFRESH_ERRORS = (search.SearchUnavailableError, *search.TYPESENSE_ERRORS)


class Command(BaseCommand):
    help = "Preview the approved legacy-topic reconciliation; pass --apply to write it."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Apply the displayed plan atomically.")

    def handle(self, *args, **options):
        try:
            plan = build_plan()
        except ReconciliationBlockedError as exc:
            raise CommandError(f"Reconciliation blocked; database unchanged:\n{exc}") from exc

        for line in describe_plan(plan):
            self.stdout.write(line)
        if not plan:
            self.stdout.write(self.style.SUCCESS("No topic changes required."))
            return
        if not options["apply"]:
            self.stdout.write(self.style.WARNING("Dry run only. Re-run with --apply to write these changes."))
            return

        changed = apply_plan(plan)
        self.stdout.write(self.style.SUCCESS(f"Applied {len(changed)} canonical topic groups."))
        try:
            indexed = search.reindex(log=self.stdout.write)
        except SEARCH_REFRESH_ERRORS:
            self.stderr.write(
                self.style.WARNING(
                    "Database reconciliation applied, but search refresh failed. "
                    "Run reindex_search when Typesense is available."
                )
            )
            return
        self.stdout.write(self.style.SUCCESS(f"Search refreshed: {indexed} documents indexed."))
