import { defineComponent, toRefs, PropType } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { Contact } from "@/models/contact";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Notary Information", type: String },
    accountNotaryContact: { default: {}, type: Object as PropType<Contact> },
    accountNotaryName: { default: "", type: String },
  },
  setup(props, ctx) {
    const { tabNumber, title, accountNotaryContact, accountNotaryName } =
      toRefs(props);
    return {};
  },
});
