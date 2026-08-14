# Changelog

All notable changes to this project are documented here.

This project follows semantic versioning:

- `MAJOR` for incompatible data model, config entry, or frontend API changes.
- `MINOR` for new adapters, new entities, or new user-visible features.
- `PATCH` for fixes, copy changes, diagnostics, and compatibility updates.

Every user-visible update must change `custom_components/network_topology/manifest.json`
and add a matching entry below.

## 0.1.3 - 2026-08-14

- Add adapter metadata for brand, model, and icon.
- Add a diagnostic topology source sensor for each configured instance with
  brand-specific icon and device registry metadata.
- Add a project icon asset for the integration package.

## 0.1.2 - 2026-08-14

- Add the custom integration translation file so setup fields show
  user-facing brand/model labels instead of raw internal keys.

## 0.1.1 - 2026-08-14

- Present topology source setup as a user-facing brand/model choice instead of
  exposing the internal adapter concept.

## 0.1.0 - 2026-08-14

- Initial HACS-compatible Network Topology custom integration.
- Add TP-Link TL-R489GP-AC local web adapter.
- Add read-only topology API, sidebar panel, Lovelace card, and
  `device_tracker` entities.
