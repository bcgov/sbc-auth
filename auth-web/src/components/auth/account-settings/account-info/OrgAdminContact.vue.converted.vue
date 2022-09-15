import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Emit, Vue } from "vue-property-decorator";
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  RoleInfo,
} from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import { AccessType } from "@/util/constants";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const activeOrgMembers = computed(
      () => ctx.root.$store.state.org.activeOrgMembers
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const syncActiveOrgMembers = () =>
      ctx.root.$store.dispatch("org/syncActiveOrgMembers");
    const activeOrgMembers = ref<Member[]>(undefined);
    const syncActiveOrgMembers = ref<() => Member[]>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const getActiveAdmins = computed((): Member[] => {
      return activeOrgMembers.value.filter(
        (member) => member.membershipTypeCode === MembershipType.Admin
      );
    });
    const anonAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.ANONYMOUS;
    });
    onMounted(async () => {
      syncActiveOrgMembers.value();
    });
    return {
      activeOrgMembers,
      currentOrganization,
      syncActiveOrgMembers,
      activeOrgMembers,
      syncActiveOrgMembers,
      currentOrganization,
      getActiveAdmins,
      anonAccount,
    };
  },
});
