import { defineComponent, toRefs } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
import ConfigHelper from "@/util/config-helper";
import { LDFlags } from "@/util/constants";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import { appendAccountId } from "sbc-common-components/src/util/common-util";
export default defineComponent({
  props: {
    isWide: { type: Boolean },
    isInverse: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { isWide, isInverse } = toRefs(props);
    const goToNameRequest = (): void => {
      if (LaunchDarklyService.getFlag(LDFlags.LinkToNewNameRequestApp)) {
        window.location.href = appendAccountId(
          ConfigHelper.getNameRequestUrl()
        );
      } else {
        window.location.href = appendAccountId(ConfigHelper.getNroUrl());
      }
    };
    return { goToNameRequest };
  },
});
