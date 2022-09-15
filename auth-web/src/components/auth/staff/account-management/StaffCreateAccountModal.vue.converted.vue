import { defineComponent, ref } from "@vue/composition-api";
import { Component, Emit, Vue } from "vue-property-decorator";
import { Pages, StaffCreateAccountsTypes } from "@/util/constants";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const selctedAccount = ref<string>(
      StaffCreateAccountsTypes.DIRECTOR_SEARCH
    );
    const accountTypes = ref<any>(StaffCreateAccountsTypes);
    const $refs = ref<{
      createAccountDialog: ModalDialog;
    }>(undefined);
    const open = () => {
      ctx.refs.createAccountDialog.open();
    };
    const close = () => {
      ctx.refs.createAccountDialog.close();
    };
    const createAccount = () => {
      if (selctedAccount.value === StaffCreateAccountsTypes.DIRECTOR_SEARCH) {
        ctx.root.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` });
      } else {
        ctx.root.$router.push({ path: `${Pages.STAFF_GOVM_SETUP_ACCOUNT}` });
      }
    };
    return { selctedAccount, accountTypes, $refs, open, close, createAccount };
  },
});
