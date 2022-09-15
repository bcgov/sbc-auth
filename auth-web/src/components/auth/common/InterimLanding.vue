import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {
    summary: { default: "", type: String },
    description: { default: "", type: String },
    icon: { default: "mdi-information-outline", type: String },
    iconColor: { default: "primary", type: String },
    showHomePageBtn: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const { summary, description, icon, iconColor, showHomePageBtn } =
      toRefs(props);
    const goHome = () => {
      ctx.root.$router.push("/");
    };
    return { goHome };
  },
});
