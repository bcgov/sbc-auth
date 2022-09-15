import { defineComponent, toRefs, PropType } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { Contact } from "@/models/contact";
import { User } from "@/models/user";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Account Administrator", type: String },
    accountUnderReviewAdmin: { default: {}, type: Object as PropType<User> },
    accountUnderReviewAdminContact: { type: Object as PropType<Contact> },
  },
  setup(props, ctx) {
    const {
      tabNumber,
      title,
      accountUnderReviewAdmin,
      accountUnderReviewAdminContact,
    } = toRefs(props);
    return {};
  },
});
