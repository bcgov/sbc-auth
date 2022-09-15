import { defineComponent, toRefs, ref, computed } from "@vue/composition-api";
import { Component, Prop } from "vue-property-decorator";
import Vue from "vue";
export default defineComponent({
  props: { type: { type: String } },
  setup(props, ctx) {
    const { type } = toRefs(props);
    const infoArray = ref<
      {
        title: string;
        description?: string;
        type?: string;
      }[]
    >([
      {
        title: "deactivateMemberRemovalTitle",
        description: "deactivateMemberRemovalDesc",
      },
      {
        title: "businessRemovalTitle",
        description: "businessRemovalDesc",
      },
      {
        title: "padRemovalTitle",
        type: "PREMIUM",
      },
    ]);
    const info = computed(() => {
      return infoArray.value.filter(
        (obj) => !obj.type || obj.type === type.value
      );
    });
    return { infoArray, info };
  },
});
