/** @odoo-module **/
import { Component, onWillStart, markup, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { View } from "@web/views/view";
import { escape } from "@web/core/utils/strings";
export class ImportVietNamAddress extends Component {
  setup() {
    this.baseViewProps = {
      display: { searchPanel: false },
      editable: false, // readonly
      noBreadcrumbs: true,
      showButtons: false,
    };
    this.orm = useService("orm");
    this.state = useState({});

    this.user = useService("user");
    // this.actionService = useService("action");
    onWillStart(async () => await this.initialize());
  }

  async initialize() {
    let data = await this.orm.searchRead(
      "ir.model.data",
      [["name", "=", "view_import_vietnam_address_form"]],
      ["res_id"]
    );
    this.state.viewId = data[0].res_id;
    data = await this.orm.searchRead(
      "ir.model.data",
      [["name", "=", "view_vietnam_address_overview_tree"]],
      ["res_id"]
    );
    this.state.viewIdList = data[0].res_id;

    data = await this.orm.searchRead(
      "ir.model.data",
      [["name", "=", "vietnam_address_overview_search"]],
      ["res_id"]
    );
    this.state.searchViewId = data[0].res_id;
  }

  get viewProps() {
    const props = {
      ...this.baseViewProps,
      context: {},
      domain: [],
      resModel: "import.vietnam.address",
      // Ẩn checkbox
      type: "form",
      viewId: this.state.viewId,
    };
    return props;
  }

  get viewPropsList() {
    const props = {
      ...this.baseViewProps,
      context: {},
      domain: [],
      resModel: "vietnam.address.overview",
      // Ẩn checkbox
      type: "list",
      viewId: this.state.viewIdList,
      allowSelectors: false,
      searchViewId: this.state.searchViewId,
    };
    return props;
  }
}

ImportVietNamAddress.template = "vietNamAddressAutofill.import_vietnam_address";
ImportVietNamAddress.components = { View };
ImportVietNamAddress.props = {};
registry
  .category("actions")
  .add("vietNamAddressAutofill.import_vietnam_address", ImportVietNamAddress);
