import { LitElement, css, html } from "./vendor/lit.bundle.mjs";

class NetworkTopologyPanel extends LitElement {
  static properties = {
    hass: { attribute: false },
    panel: { attribute: false },
    _rendererReady: { state: true },
    _rendererError: { state: true },
  };

  constructor() {
    super();
    this._rendererReady = false;
    this._rendererError = "";
  }

  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
      color: var(--primary-text-color, #1f2933);
      background: var(--primary-background-color, #f7f8fa);
    }

    .page {
      max-width: 1640px;
      margin: 0 auto;
      padding: 20px;
    }

    .error,
    .loading {
      padding: 20px;
      color: var(--secondary-text-color, #6b7280);
    }

    .error {
      color: var(--error-color, #db4437);
    }
  `;

  firstUpdated() {
    this._loadRenderer();
  }

  updated(changedProperties) {
    if (changedProperties.has("hass")) {
      this._syncCard();
    }
  }

  render() {
    if (this._rendererError) {
      return html`<main class="page"><div class="error">Failed to load topology renderer: ${this._rendererError}</div></main>`;
    }
    if (!this._rendererReady) {
      return html`<main class="page"><div class="loading">Loading topology renderer...</div></main>`;
    }
    return html`
      <main class="page">
        <network-topology-graph-card></network-topology-graph-card>
      </main>
    `;
  }

  async _loadRenderer() {
    try {
      await import("./network-topology-graph-card.js?v=20260814-loading-state");
      this._rendererReady = true;
      await this.updateComplete;
      this._syncCard();
    } catch (error) {
      this._rendererError = error?.message || String(error);
    }
  }

  _syncCard() {
    const card = this.renderRoot.querySelector("network-topology-graph-card");
    if (!card) {
      return;
    }
    card.setConfig({
      title: "Network Topology",
      api_path: "network_topology/topology",
    });
    card.hass = this.hass;
  }
}

for (const tagName of ["network-topology-panel", "network-topology"]) {
  if (!customElements.get(tagName)) {
    customElements.define(tagName, class extends NetworkTopologyPanel {});
  }
}
