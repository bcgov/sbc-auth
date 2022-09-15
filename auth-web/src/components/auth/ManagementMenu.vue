import { defineComponent, computed, toRefs, ref } from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
import OrgModule from "@/store/modules/org";
import { Organization } from "@/models/Organization";
import { User } from "@/models/user";
import UserModule from "@/store/modules/user";
import { getModule } from "vuex-module-decorators";
import { mapState } from "vuex";
export default defineComponent({
  name: "ManagementMenu",
  props: { menu: { type: null } },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const { menu } = toRefs(props);
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const userStore = ref(getModule(UserModule, ctx.root.$store));
    const currentOrganization = ref<Organization>(undefined);
    return { currentOrganization, orgStore, userStore, currentOrganization };
  },
});
