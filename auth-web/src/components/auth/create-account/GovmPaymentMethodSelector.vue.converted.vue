import { defineComponent, ref } from "@vue/composition-api";
import { Component, Emit, Mixins, Prop } from "vue-property-decorator";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import GLPaymentForm from "@/components/auth/common/GLPaymentForm.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
export default defineComponent({
  components: {
    ConfirmCancelButton,
    GLPaymentForm,
  },
  props: {},
  setup(_props, ctx) {
    const isGLValid = ref<boolean>(false);
    const isGLInfoValid = (isValid) => {
      isGLValid.value = isValid;
    };
    const goBack = () => {
      stepBack();
    };
    const next = () => {
      stepForward();
    };
    const cancel = () => {
      ctx.root.$router.push("/");
    };
    return { isGLValid, isGLInfoValid, goBack, next, cancel };
  },
});
