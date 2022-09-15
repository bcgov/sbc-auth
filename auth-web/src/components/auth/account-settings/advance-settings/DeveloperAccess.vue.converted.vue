import { defineComponent, ref } from "@vue/composition-api";
import { Component, Mixins } from "vue-property-decorator";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import ConfigHelper from "@/util/config-helper";
import ExistingAPIKeys from "@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue";
export default defineComponent({
  components: {
    ExistingAPIKeys,
  },
  props: {},
  setup(_props, ctx) {
    const APIDOCUMENTATION_URL = ref(ConfigHelper.apiDocumentationUrl() || "");
    return { APIDOCUMENTATION_URL };
  },
});
