import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
export default defineComponent({
  props: {
    redirectUrl: { type: String },
    isWide: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { redirectUrl, isWide } = toRefs(props);
    return {};
  },
});
