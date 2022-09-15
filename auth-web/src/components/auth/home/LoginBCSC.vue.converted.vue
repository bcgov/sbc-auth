import { defineComponent, ref } from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
export default defineComponent({
  name: "LoginBCSC",
  props: {},
  setup(_props, ctx) {
    const bcscRedirectUrl = ref(
      "https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card"
    );
    const login = () => {
      ctx.root.$router.push("/signin/bcsc/createaccount");
    };
    return { bcscRedirectUrl, login };
  },
});
