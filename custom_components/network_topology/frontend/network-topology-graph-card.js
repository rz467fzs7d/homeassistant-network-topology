import * as echarts from "./echarts.esm.min.js";

const DEFAULT_API_PATH = "network_topology/topology";
const DEBUG_PREFIX = "[network-topology]";

class NetworkTopologyGraphCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._topology = undefined;
    this._loading = false;
    this._error = "";
    this._search = "";
    this._showLabels = true;
    this._chart = undefined;
    this._resizeObserver = undefined;
    this._renderRetry = 0;
    this._renderFrame = undefined;
  }

  static getStubConfig() {
    return {
      title: "Network Topology",
      api_path: DEFAULT_API_PATH,
    };
  }

  setConfig(config) {
    const nextConfig = {
      title: "Network Topology",
      api_path: DEFAULT_API_PATH,
      ...config,
    };
    const configChanged = JSON.stringify(this._config) !== JSON.stringify(nextConfig);
    this._config = nextConfig;
    this._debug("setConfig", { config: this._config, configChanged });
    if (configChanged || !this.shadowRoot.querySelector("ha-card")) {
      this._render();
      this._scheduleRenderChart("setConfig");
    }
  }

  set hass(hass) {
    this._hass = hass;
    this._debug("hass assigned", { hasTopology: Boolean(this._topology), loading: this._loading });
    if (!this._topology && !this._loading) {
      this._fetchTopology();
    }
  }

  connectedCallback() {
    this._render();
    this._resizeObserver = new ResizeObserver(() => this._chart?.resize());
    const graph = this.shadowRoot?.querySelector(".graph");
    if (graph) {
      this._resizeObserver.observe(graph);
    }
  }

  disconnectedCallback() {
    this._resizeObserver?.disconnect();
    if (this._renderFrame) {
      cancelAnimationFrame(this._renderFrame);
      this._renderFrame = undefined;
    }
    this._chart?.dispose();
    this._chart = undefined;
  }

  getCardSize() {
    return 8;
  }

  async _fetchTopology() {
    if (!this._hass) {
      this._debug("skip fetch: missing hass");
      return;
    }
    this._loading = true;
    this._error = "";
    this._render();
    try {
      this._debug("fetch topology start", { apiPath: this._config.api_path });
      this._topology = await this._hass.callApi("GET", this._config.api_path);
      this._debug("fetch topology success", {
        source: this._topology?.source,
        groups: this._topology?.groups?.length || 0,
        devices: this._topology?.devices?.length || 0,
      });
    } catch (error) {
      this._error = this._errorMessage(error);
      this._debug("fetch topology failed", { error, message: this._error });
    } finally {
      this._loading = false;
      this._render();
      this._scheduleRenderChart("fetch complete");
    }
  }

  _render() {
    const summary = this._summary();
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          color: var(--primary-text-color);
          --network-node-router: var(--primary-color, #03a9f4);
          --network-node-ap: var(--cyan-color, #26c6da);
          --network-node-device: var(--success-color, #4caf50);
          --network-node-unknown: var(--warning-color, #ff9800);
          --network-node-offline: var(--error-color, #db4437);
        }
        ha-card {
          overflow: hidden;
          min-height: 620px;
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 16px;
          padding: 16px 20px 8px;
        }
        .title {
          margin: 0;
          font-size: 20px;
          line-height: 1.2;
          font-weight: 650;
          letter-spacing: 0;
        }
        .subtitle {
          margin-top: 4px;
          color: var(--secondary-text-color);
          font-size: 12px;
        }
        .toolbar {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 8px;
          flex-wrap: wrap;
        }
        .search {
          height: 36px;
          width: 220px;
          max-width: 32vw;
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          padding: 0 10px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font: inherit;
        }
        button {
          min-height: 36px;
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          padding: 0 12px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font: inherit;
          cursor: pointer;
        }
        button:disabled {
          cursor: progress;
          opacity: 0.68;
        }
        .stats {
          display: flex;
          gap: 8px;
          padding: 0 20px 10px;
          flex-wrap: wrap;
        }
        .metric {
          min-width: 86px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 7px 10px;
          background: color-mix(in srgb, var(--card-background-color) 88%, var(--primary-color));
        }
        .metric strong {
          display: block;
          font-size: 16px;
          line-height: 1.1;
        }
        .metric span {
          display: block;
          margin-top: 2px;
          color: var(--secondary-text-color);
          font-size: 11px;
        }
        .status {
          padding: 0 20px 8px;
          color: var(--secondary-text-color);
          font-size: 12px;
        }
        .status.error {
          color: var(--error-color);
        }
        .progress {
          height: 3px;
          margin: 0 20px 10px;
          overflow: hidden;
          border-radius: 999px;
          background: color-mix(in srgb, var(--primary-color) 14%, transparent);
        }
        .progress::before {
          content: "";
          display: block;
          width: 42%;
          height: 100%;
          border-radius: inherit;
          background: var(--primary-color);
          animation: tplink-progress 1.15s ease-in-out infinite;
        }
        @keyframes tplink-progress {
          0% {
            transform: translateX(-110%);
          }
          100% {
            transform: translateX(250%);
          }
        }
        .graph {
          position: relative;
          height: min(68vh, 760px);
          min-height: 520px;
          margin: 0 12px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          background: var(--card-background-color);
        }
        .placeholder {
          position: absolute;
          inset: 0;
          display: grid;
          place-items: center;
          padding: 24px;
          text-align: center;
          color: var(--secondary-text-color);
          background:
            radial-gradient(circle at center, color-mix(in srgb, var(--primary-color) 8%, transparent) 0 1px, transparent 1px) 0 0 / 20px 20px,
            var(--card-background-color);
        }
        .placeholder-card {
          max-width: 460px;
          border: 1px solid var(--divider-color);
          border-radius: 10px;
          padding: 18px 20px;
          background: color-mix(in srgb, var(--card-background-color) 94%, var(--primary-color));
          box-shadow: var(--ha-card-box-shadow, none);
        }
        .placeholder-title {
          margin: 0 0 6px;
          color: var(--primary-text-color);
          font-size: 15px;
          font-weight: 650;
        }
        .placeholder-text {
          margin: 0;
          font-size: 12px;
          line-height: 1.45;
        }
        .spinner {
          width: 28px;
          height: 28px;
          margin: 0 auto 12px;
          border: 3px solid color-mix(in srgb, var(--primary-color) 18%, transparent);
          border-top-color: var(--primary-color);
          border-radius: 999px;
          animation: network-spin 0.9s linear infinite;
        }
        @keyframes network-spin {
          to {
            transform: rotate(360deg);
          }
        }
        .placeholder.error .placeholder-card {
          border-color: color-mix(in srgb, var(--error-color) 42%, var(--divider-color));
          background: color-mix(in srgb, var(--card-background-color) 86%, var(--error-color));
        }
        .placeholder.error .placeholder-title {
          color: var(--error-color);
        }
        @media (max-width: 720px) {
          .header {
            flex-direction: column;
          }
          .toolbar {
            justify-content: flex-start;
          }
          .search {
            width: min(100%, 280px);
            max-width: none;
          }
        }
      </style>
      <ha-card>
        <div class="header">
          <div>
            <h2 class="title">${this._escape(this._config.title)}</h2>
            <div class="subtitle">TP-Link AC/AP topology rendered as a Home Assistant-style knowledge graph</div>
          </div>
          <div class="toolbar">
            <input class="search" type="search" placeholder="Search" value="${this._escapeAttribute(this._search)}" />
            <button class="labels ${this._showLabels ? "active" : ""}" type="button">Labels</button>
            <button class="refresh" type="button" ${this._loading ? "disabled" : ""}>${this._loading ? "Refreshing..." : "Refresh"}</button>
          </div>
        </div>
        <div class="stats">
          <div class="metric"><strong>${summary.wired}</strong><span>wired</span></div>
          <div class="metric"><strong>${summary.wireless}</strong><span>wireless</span></div>
          <div class="metric"><strong>${summary.unknown}</strong><span>unknown/raw</span></div>
        </div>
        <div class="status ${this._error ? "error" : ""}">
          ${this._statusText()}
        </div>
        ${this._loading ? `<div class="progress" role="progressbar" aria-label="Refreshing topology"></div>` : ""}
        <div class="graph">${this._graphPlaceholder()}</div>
      </ha-card>
    `;
    this.shadowRoot.querySelector(".refresh")?.addEventListener("click", () => this._fetchTopology());
    this.shadowRoot.querySelector(".labels")?.addEventListener("click", () => {
      this._showLabels = !this._showLabels;
      this._render();
      this._scheduleRenderChart("labels toggle");
    });
    this.shadowRoot.querySelector(".search")?.addEventListener("input", (event) => {
      this._search = event.target.value || "";
      this._scheduleRenderChart("search");
    });
    this._observeGraph();
  }

  _scheduleRenderChart(reason) {
    if (!this._topology) {
      return;
    }
    if (this._renderFrame) {
      cancelAnimationFrame(this._renderFrame);
    }
    this._debug("schedule renderChart", { reason });
    this._renderFrame = requestAnimationFrame(() => {
      this._renderFrame = undefined;
      this._renderChart();
    });
  }

  _renderChart() {
    const graph = this.shadowRoot?.querySelector(".graph");
    if (!graph || !this._topology) {
      this._debug("skip renderChart", { hasGraph: Boolean(graph), hasTopology: Boolean(this._topology) });
      return;
    }
    const graphRect = graph.getBoundingClientRect();
    if (!graph.clientWidth || !graph.clientHeight || !graphRect.width || !graphRect.height) {
      if (this._renderRetry < 20) {
        this._renderRetry += 1;
        this._debug("defer renderChart: graph has no size", {
          attempt: this._renderRetry,
          width: graph.clientWidth,
          height: graph.clientHeight,
          rectWidth: graphRect.width,
          rectHeight: graphRect.height,
        });
        this._scheduleRenderChart("graph-size-wait");
      } else {
        this._debug("renderChart aborted: graph still has no size");
      }
      return;
    }
    this._renderRetry = 0;
    const graphData = this._networkData();
    this._debug("renderChart start", {
      width: graph.clientWidth,
      height: graph.clientHeight,
      rectWidth: graphRect.width,
      rectHeight: graphRect.height,
      nodes: graphData.nodes.length,
      links: graphData.links.length,
      categories: graphData.categories.map((category) => category.name),
    });
    try {
      if (!this._chart || this._chart.isDisposed?.() || this._chart.getDom?.() !== graph) {
        this._chart?.dispose();
        this._chart = echarts.init(graph);
        this._debug("echarts initialized");
      }
      this._chart.setOption(this._chartOptions(graphData), true);
      this._chart.resize();
      this._debug("renderChart complete");
    } catch (error) {
      this._error = error?.message || String(error);
      this._debug("renderChart failed", error);
      this._render();
    }
  }

  _chartOptions(graphData = this._networkData()) {
    return {
      tooltip: {
        trigger: "item",
        confine: true,
        formatter: (params) => this._tooltip(params),
      },
      legend: {
        show: true,
        bottom: 8,
        data: graphData.categories.map((category) => category.name),
      },
      dataZoom: {
        type: "inside",
        filterMode: "none",
      },
      series: [
        {
          id: "network",
          type: "graph",
          layout: "force",
          top: 36,
          right: 64,
          bottom: 56,
          left: 64,
          roam: true,
          draggable: true,
          focusNodeAdjacency: true,
          categories: graphData.categories,
          data: graphData.nodes,
          links: graphData.links,
          edgeSymbol: ["none", "none"],
          force: {
            repulsion: [160, 360],
            gravity: 0.08,
            edgeLength: [90, 210],
            layoutAnimation: true,
          },
          label: {
            show: this._showLabels,
            position: "right",
            formatter: (params) => params.data.context ? `${params.data.name}\n${params.data.context}` : params.data.name,
            color: this._cssVar("--primary-text-color", "#212121"),
            fontSize: 11,
          },
          lineStyle: {
            color: "source",
            curveness: 0.08,
            opacity: 0.72,
          },
          emphasis: {
            focus: "adjacency",
            lineStyle: {
              width: 3,
            },
          },
        },
      ],
    };
  }

  _networkData() {
    const style = getComputedStyle(this);
    const colors = {
      router: style.getPropertyValue("--network-node-router").trim() || "#03a9f4",
      ap: style.getPropertyValue("--network-node-ap").trim() || "#26c6da",
      device: style.getPropertyValue("--network-node-device").trim() || "#4caf50",
      unknown: style.getPropertyValue("--network-node-unknown").trim() || "#ff9800",
      offline: style.getPropertyValue("--network-node-offline").trim() || "#db4437",
      line: this._cssVar("--secondary-text-color", "#607d8b"),
    };
    const categories = [
      { name: "AC / Router", symbol: "roundRect", itemStyle: { color: colors.router } },
      { name: "Access Point", symbol: "circle", itemStyle: { color: colors.ap } },
      { name: "Device", symbol: "circle", itemStyle: { color: colors.device } },
      { name: "Unknown / Raw", symbol: "circle", itemStyle: { color: colors.unknown } },
      { name: "Offline", symbol: "circle", itemStyle: { color: colors.offline } },
    ];
    const root = this._topology.root || {};
    const rootId = root.id || "tplink-ac";
    const nodes = [
      this._node({
        id: rootId,
        name: root.label || "TP-Link AC",
        context: root.ip || "",
        category: 0,
        value: 5,
        symbol: "roundRect",
        symbolSize: 58,
        color: colors.router,
      }),
    ];
    const links = [];
    const groups = this._topology.groups || [];
    const devices = this._topology.devices || [];

    const renderableGroupIds = new Set();
    groups.forEach((group) => {
      if (group.kind === "wired") {
        return;
      }
      renderableGroupIds.add(group.id);
      nodes.push(this._node({
        id: group.id,
        name: group.label,
        context: group.ip || `${group.device_count || 0} devices`,
        category: 1,
        value: 4,
        symbol: "circle",
        symbolSize: 38,
        color: colors.ap,
      }));
      links.push({
        source: rootId,
        target: group.id,
        value: group.device_count || 1,
        symbolSize: 6,
        lineStyle: {
          width: 2.2,
          color: colors.line,
          type: "solid",
        },
      });
    });

    devices.forEach((device, index) => {
      const unknown = !device.known || /^unknown-|^raw-/.test(device.name || "");
      const offline = device.state && device.state !== "online";
      const category = offline ? 4 : unknown ? 3 : 2;
      const groupId = device.group_id || "wired-lan";
      const isWireless = device.scope === "wireless" && renderableGroupIds.has(groupId);
      nodes.push(this._node({
        id: device.id || device.mac || device.ip || `device-${index}`,
        name: device.name || device.raw_name || device.ip || "unknown",
        context: device.ip || device.mac || "",
        category,
        value: 1,
        symbol: "circle",
        symbolSize: unknown ? 22 : 20,
        color: offline ? colors.offline : unknown ? colors.unknown : colors.device,
        meta: device,
      }));
      links.push({
        source: isWireless ? groupId : rootId,
        target: device.id || device.mac || device.ip || `device-${index}`,
        value: this._rssiValue(device.rssi),
        symbolSize: 4,
        lineStyle: {
          width: isWireless ? 1 : 1.6,
          color: colors.line,
          type: isWireless ? "dashed" : "solid",
          opacity: offline ? 0.35 : 0.68,
        },
      });
    });

    return { categories, nodes, links };
  }

  _observeGraph() {
    const graph = this.shadowRoot?.querySelector(".graph");
    if (!graph || !this._resizeObserver) {
      return;
    }
    this._resizeObserver.disconnect();
    this._resizeObserver.observe(graph);
  }

  _node({ id, name, context, category, value, symbol, symbolSize, color, fixed, x, y, meta }) {
    const match = this._matchesSearch({ id, name, context, meta });
    return {
      id,
      name,
      context,
      category,
      value,
      symbol,
      symbolSize: match ? symbolSize + 6 : symbolSize,
      fixed,
      x,
      y,
      meta,
      itemStyle: {
        color,
        opacity: this._search && !match ? 0.22 : 1,
        borderColor: match && this._search ? this._cssVar("--primary-text-color", "#212121") : color,
        borderWidth: match && this._search ? 3 : 1,
      },
    };
  }

  _matchesSearch({ id, name, context, meta }) {
    if (!this._search) {
      return false;
    }
    const haystack = [
      id,
      name,
      context,
      meta?.raw_name,
      meta?.ip,
      meta?.mac,
      meta?.access_point,
      meta?.ssid,
      meta?.radio,
      meta?.rssi,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(this._search.toLowerCase());
  }

  _tooltip(params) {
    const data = params.data || {};
    if (params.dataType === "edge") {
      return `${this._escape(data.source)} -> ${this._escape(data.target)}`;
    }
    const meta = data.meta;
    if (!meta) {
      return `<strong>${this._escape(data.name || data.id)}</strong><br>${this._escape(data.context || "")}`;
    }
    return [
      `<strong>${this._escape(meta.name || data.name)}</strong>`,
      meta.ip ? `IP: ${this._escape(meta.ip)}` : "",
      meta.mac ? `MAC: ${this._escape(meta.mac)}` : "",
      meta.access_point ? `AP: ${this._escape(meta.access_point)}` : "",
      meta.ssid ? `SSID: ${this._escape(meta.ssid)}` : "",
      meta.radio ? `Band: ${this._escape(meta.radio)}` : "",
      meta.rssi ? `RSSI: ${this._escape(meta.rssi)}` : "",
      meta.state ? `State: ${this._escape(meta.state)}` : "",
    ].filter(Boolean).join("<br>");
  }

  _summary() {
    const devices = this._topology?.devices || [];
    return {
      wired: devices.filter((device) => device.scope === "wired").length,
      wireless: devices.filter((device) => device.scope === "wireless").length,
      unknown: devices.filter((device) => !device.known || /^unknown-|^raw-/.test(device.name || "")).length,
    };
  }

  _statusText() {
    if (this._error) {
      return `Failed to load topology: ${this._escape(this._error)}`;
    }
    if (this._loading) {
      return this._topology ? "Refreshing topology from TP-Link web..." : "Loading topology from TP-Link web...";
    }
    const refresh = this._topology?.refresh;
    const generated = this._topology?.generated_at;
    const updated = refresh?.last_success_at || generated;
    if (!updated) {
      return "Topology has not loaded yet.";
    }
    const date = new Date(updated);
    const label = Number.isNaN(date.getTime()) ? updated : date.toLocaleString();
    const source = this._topology?.source || "unknown source";
    const warning = refresh && refresh.ok === false ? `; refresh failed: ${refresh.last_error}` : "";
    return `Updated ${label}; source: ${source}${warning}`;
  }

  _graphPlaceholder() {
    if (this._loading && !this._hasRenderableTopology()) {
      return `
        <div class="placeholder loading">
          <div class="placeholder-card">
            <div class="spinner" aria-hidden="true"></div>
            <p class="placeholder-title">Loading topology</p>
            <p class="placeholder-text">Connecting to Home Assistant and reading the latest TP-Link AC/AP data.</p>
          </div>
        </div>
      `;
    }
    if (this._error && !this._hasRenderableTopology()) {
      return `
        <div class="placeholder error">
          <div class="placeholder-card">
            <p class="placeholder-title">Topology is unavailable</p>
            <p class="placeholder-text">${this._escape(this._error)}</p>
          </div>
        </div>
      `;
    }
    if (!this._hasRenderableTopology()) {
      return `
        <div class="placeholder">
          <div class="placeholder-card">
            <p class="placeholder-title">Waiting for topology data</p>
            <p class="placeholder-text">The integration has not returned network devices yet.</p>
          </div>
        </div>
      `;
    }
    return "";
  }

  _hasRenderableTopology() {
    return Boolean(this._topology && (this._topology.root || (this._topology.devices || []).length));
  }

  _errorMessage(error) {
    if (!error) {
      return "Unknown error";
    }
    if (typeof error === "string") {
      return error;
    }
    const candidates = [
      error.message,
      error.error,
      error.code,
      error.statusText,
      error.body?.message,
      error.body?.error,
    ].filter(Boolean);
    if (candidates.length) {
      return candidates.join(": ");
    }
    try {
      return JSON.stringify(error);
    } catch (_err) {
      return String(error);
    }
  }

  _rssiValue(rssi) {
    if (!rssi) {
      return 1;
    }
    const value = Math.abs(parseInt(String(rssi).replace("dBm", ""), 10));
    if (Number.isNaN(value)) {
      return 1;
    }
    return Math.max(1, 100 - value);
  }

  _cssVar(name, fallback) {
    return getComputedStyle(this).getPropertyValue(name).trim() || fallback;
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _escapeAttribute(value) {
    return this._escape(value).replaceAll("`", "&#096;");
  }

  _debug(message, details) {
    console.debug(DEBUG_PREFIX, message, details || "");
  }
}

if (!customElements.get("network-topology-graph-card")) {
  customElements.define("network-topology-graph-card", NetworkTopologyGraphCard);
}
