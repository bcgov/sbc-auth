import { defineComponent, ref, onMounted } from "@vue/composition-api";
import { Component, Emit, Mixins, Prop, Vue } from "vue-property-decorator";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { User } from "@/models/user";
import { namespace } from "vuex-class";
const userModule = namespace("user");
export default defineComponent({
  components: {
    ConfirmCancelButton,
  },
  props: {},
  setup(_props, ctx) {
    const emailAddress = ref("");
    const confirmedEmailAddress = ref("");
    const $refs = ref<{
      form: HTMLFormElement;
    }>(undefined);
    const createAccount = () => {};
    const cancel = () => {
      ctx.root.$router.push("/");
    };
    const goBack = () => {
      stepBack();
    };
    onMounted(async () => {
      await getUserProfile("@me");
      emailAddress.value = userProfile?.email || "";
      emailAddress.value = confirmedEmailAddress.value =
        userProfile?.email || "";
    });
    return {
      emailAddress,
      confirmedEmailAddress,
      $refs,
      createAccount,
      cancel,
      goBack,
    };
  },
});
