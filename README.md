# Bin collection calendar

A daily GitHub Action fetches North Yorkshire Council (Hambleton) bin collection dates and publishes them as an ICS feed:

`https://tomtom800.github.io/bins/bins.ics`

Subscribe on Mac: Calendar → File → New Calendar Subscription → paste the URL → set Location to iCloud (so it syncs to iPhone) and Auto-refresh to Every day.

The property UPRN is stored as the `UPRN` repository secret. To run it manually, use Actions → Update bin calendar → Run workflow.
