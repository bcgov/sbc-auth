import { defineComponent, toRefs, ref, PropType } from "@vue/composition-api";
import { AccessType, Account } from "@/util/constants";
import { Component, Prop, Vue } from "vue-property-decorator";
import { Address } from "@/models/address";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Account Information", type: String },
    accountUnderReview: { default: {}, type: Object as PropType<any> },
    accountUnderReviewAddress: {
      default: null,
      type: Object as PropType<Address>,
    },
  },
  setup(props, ctx) {
    const { tabNumber, title, accountUnderReview, accountUnderReviewAddress } =
      toRefs(props);
    const AccessType = ref(AccessType);
    const Account = ref(Account);
    return { AccessType, Account };
  },
});
