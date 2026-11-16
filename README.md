# Bin collection calendar

A daily GitHub Action fetches North Yorkshire Council (Hambleton) bin collection dates and publishes them as an ICS feed:

`https://raw.githubusercontent.com/tomtom800/bins/main/bins.ics`

Subscribe on Mac: Calendar → File → New Calendar Subscription → paste the URL → set Location to iCloud (so it syncs to iPhone) and Auto-refresh to Every day.

The property UPRN is stored as the `UPRN` repository secret. It also runs whenever the script or workflow changes. To run it manually, use Actions → Update bin calendar → Run workflow.
