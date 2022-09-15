import { defineComponent } from "@vue/composition-api";
import Component from "vue-class-component";
import Vue from "vue";
export default defineComponent({
  name: "DateMixin",
  props: {},
  setup(_props, ctx) {
    const dateToPacificDate = (date: Date): string => {
      let dateStr = date.toLocaleDateString("en-CA", {
        timeZone: "America/Vancouver",
        month: "long",
        day: "numeric",
        year: "numeric",
      });
      dateStr = dateStr.replace(".", "");
      return dateStr;
    };
    return { dateToPacificDate };
  },
});
