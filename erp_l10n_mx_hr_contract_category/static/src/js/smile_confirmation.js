/** @odoo-module **/


import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import Dialog from 'web.Dialog';

patch(FormController.prototype, "erp_l10n_mx_hr_contract_category", {
    setup() {
        this._super(...arguments);
        this.rpc = useService("rpc");
    },
    rpc_call(model, nameFunction, record_id, values) {
        return this.rpc("/web/dataset/call_kw/base/" + nameFunction, {
            model: model,
            method: 'create',
            args: [[record_id], values],
            kwargs: {},
        });
    },

    async saveButtonClicked(params = {}) {
        const self = this;
        let index = 0;
        const record = this.model.root;
        const modelName = record['resModel'] ? record['resModel'] : false;
        const record_id = (record && record.data && record.data.id) ? record.data.id : false
        const recordID = record.__bm_handle__;
        const localData = self.model.__bm__.localData[recordID];
        const changes = localData._changes || {};

        display_popup(true,record['resModel'],changes);

        async function save() {
            let saved = false;

            if (self.props.saveRecord) {
                saved = await self.props.saveRecord(record, params);
            } else {
                saved = await record.save();
            }
            self.enableButtons();
            if (saved && self.props.onSave) {
                self.props.onSave(record, params);
            }
            return saved;
        }

        function display_popup(popup_values,model,changes){
            new Promise(function (resolve, reject) {
                    save();
                    if(model == 'hr.contract.category'){
                        if(changes['code'] != false && changes['name'] != false )
                            Dialog.alert(self, "Una vez creada la categoría, se requiere ir al proceso de Modificación de Salarios NÓMINA > PROCESOS DE NÓMINA > MODIFICACIÓN DE SALARIO", {title: "Confirmión"});
                    }



            });
        }
    }
});

