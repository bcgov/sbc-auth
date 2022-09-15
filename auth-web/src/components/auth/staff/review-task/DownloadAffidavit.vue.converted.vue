import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Download Affidavit", type: String },
    subTitle: {
      default:
        "Download the notarized affidavit associated with this account to verify the account creators identity and associated information.",
      type: String,
    },
    affidavitName: { default: "", type: String },
  },
  setup(props, ctx) {
    const { tabNumber, title, subTitle, affidavitName } = toRefs(props);
    return {};
  },
});
