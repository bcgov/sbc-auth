import { defineComponent, computed, ref } from "@vue/composition-api";
import { Component, Emit, Mixins } from "vue-property-decorator";
import { Organization } from "@/models/Organization";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { mapState } from "vuex";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentOrganization = ref<Organization>(undefined);
    const isAcknowledged = ref<boolean>(false);
    const proceedToPayment = async () => {};
    const goBack = () => {
      stepBack();
    };
    return {
      currentOrganization,
      currentOrganization,
      isAcknowledged,
      proceedToPayment,
      goBack,
    };
  },
});
