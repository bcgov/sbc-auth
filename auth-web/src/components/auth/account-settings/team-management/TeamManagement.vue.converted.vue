import {
  defineComponent,
  computed,
  toRefs,
  onMounted,
} from "@vue/composition-api";
import { AccessType, Role } from "@/util/constants";
import { Component, Mixins, Prop } from "vue-property-decorator";
import AnonymousUserManagement from "@/components/auth/account-settings/team-management/AnonymousUserManagement.vue";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import UserManagement from "@/components/auth/account-settings/team-management/UserManagement.vue";
import { mapState } from "vuex";
export default defineComponent({
  components: {
    UserManagement,
    AnonymousUserManagement,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const { orgId } = toRefs(props);
    const isAnonymousAccount = (): boolean => {
      return (
        currentOrganization.value &&
        currentOrganization.value.accessType === AccessType.ANONYMOUS
      );
    };
    onMounted(async () => {
      if (isAnonymousAccount() && !currentUser.roles.includes(Role.Staff)) {
        redirectTo(getNextPageUrl());
      }
    });
    return { currentMembership, currentOrganization, isAnonymousAccount };
  },
});
