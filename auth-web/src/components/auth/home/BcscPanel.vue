import { defineComponent, toRefs, ref, PropType } from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import LearnMoreButton from "@/components/auth/common/LearnMoreButton.vue";
import { User } from "@/models/user";
export default defineComponent({
  components: {
    LearnMoreButton,
  },
  props: { userProfile: { type: Object as PropType<User> } },
  setup(props, ctx) {
    const { userProfile } = toRefs(props);
    const cardSetUpUrl = ref(
      "https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup"
    );
    const learnMoreUrl = ref(
      "https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup"
    );
    const secureBulletPoints = ref<Array<any>>([
      {
        text: "A mobile card is a representation of your BC Services Card on your mobile device. It's used to prove who you are when you log in to access government services online.",
      },
      {
        text: "Only your name and a unique identifier is stored on the mobile device.",
      },
    ]);
    const easeBulletPoints = ref<Array<any>>([
      {
        text: "You can verify your identity by video right from your mobile device. You don't need to go in person unless you can't verify by video.",
      },
    ]);
    const emitLogin = () => {};
    const emitAccountDialog = () => {};
    return {
      cardSetUpUrl,
      learnMoreUrl,
      secureBulletPoints,
      easeBulletPoints,
      emitLogin,
      emitAccountDialog,
    };
  },
});
