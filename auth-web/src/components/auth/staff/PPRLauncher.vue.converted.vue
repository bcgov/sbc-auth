import { defineComponent, ref, computed, watch } from "@vue/composition-api";
import { Component, Watch } from "vue-property-decorator";
import ConfigHelper from "@/util/config-helper";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import Vue from "vue";
import { namespace } from "vuex-class";
const userModule = namespace("user");
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const title = ref("");
    const text = ref("");
    const img = ref("");
    const pprUrl = computed((): string => {
      return ConfigHelper.getPPRWebUrl();
    });
    const getImgUrl = (img) => {
      const images = require.context("@/assets/img/");
      return images("./" + img);
    };
    const assignAssetContent = (): void => {
      const roles = currentUser?.roles;
      switch (true) {
        case roles.includes("ppr") && roles.includes("mhr"):
          img.value = "AssetsRegistries_dashboard.jpg";
          title.value = ctx.root.$t("assetLauncherTitle").toString();
          text.value = ctx.root.$t("assetLauncherText").toString();
          break;
        case roles.includes("mhr"):
          img.value = "ManufacturedHomeRegistry_dashboard.jpg";
          title.value = ctx.root.$t("mhrLauncherTitle").toString();
          text.value = ctx.root.$t("mhrLauncherText").toString();
          break;
        default:
          img.value = "PPR_dashboard_thumbnail_image.jpg";
          title.value = ctx.root.$t("pprLauncherTitle").toString();
          text.value = ctx.root.$t("pprLauncherText").toString();
          break;
      }
    };
    watch(currentUser, assignAssetContent, { deep: true, immediate: true });
    return { title, text, img, pprUrl, getImgUrl, assignAssetContent };
  },
});
