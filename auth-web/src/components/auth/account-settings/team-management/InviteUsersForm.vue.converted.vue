import { defineComponent, computed, ref } from "@vue/composition-api";
import { AccessType, LoginSource } from "@/util/constants";
import { Component, Emit, Vue } from "vue-property-decorator";
import {
  Member,
  MembershipType,
  Organization,
  RoleInfo,
} from "@/models/Organization";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { Invitation } from "@/models/Invitation";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import OrgModule from "@/store/modules/org";
import TeamManagementMixin from "../../mixins/TeamManagementMixin.vue";
import { getModule } from "vuex-module-decorators";
interface InvitationInfo {
  emailAddress: string;
  role: RoleInfo;
  selectedRole?: RoleInfo;
}
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const pendingOrgInvitations = computed(
      () => ctx.root.$store.state.org.pendingOrgInvitations
    );
    const roleInfos = computed(() => ctx.root.$store.state.user.roleInfos);
    const createInvitation = () =>
      ctx.root.$store.dispatch("org/createInvitation");
    const resendInvitation = () =>
      ctx.root.$store.dispatch("org/resendInvitation");
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const loading = ref(false);
    const pendingOrgInvitations = ref<Invitation[]>(undefined);
    const resetInvitations = ref<() => void>(undefined);
    const createInvitation = ref<(Invitation) => Promise<void>>(undefined);
    const resendInvitation = ref<(Invitation) => Promise<void>>(undefined);
    const roleInfos = ref<RoleInfo[]>(undefined);
    const $refs = ref<{
      form: HTMLFormElement;
    }>(undefined);
    const invitations = ref<InvitationInfo[]>([]);
    const emailRules = ref(CommonUtils.emailRules(true));
    const roles = ref<RoleInfo[]>([]);
    const availableRoles = computed(() => {
      if (currentMembership.membershipTypeCode !== MembershipType.Admin) {
        return roles.value.filter((role) => role.name !== MembershipType.Admin);
      }
      return roles.value;
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const hasDuplicates = (): boolean => {
      const invitations = invitations.value.filter(
        (invitation) => invitation.emailAddress
      );
      return (
        new Set(
          invitations.map((invitation) => invitation.emailAddress.toLowerCase())
        ).size !== invitations.length
      );
    };
    const isFormValid = (): boolean => {
      return (
        invitations.value &&
        invitations.value.some((invite) => invite.emailAddress) &&
        !hasDuplicates() &&
        ctx.refs.form.validate()
      );
    };
    const removeEmail = (index: number) => {
      invitations.value.splice(index, 1);
    };
    const addEmail = () => {
      invitations.value.push({
        emailAddress: "",
        role: roles.value[0],
        selectedRole: { ...roles.value[0] },
      });
    };
    const resetForm = () => {
      invitations.value.forEach((invitation) => {
        invitation.emailAddress = "";
        invitation.role = roles.value[0];
        invitation.selectedRole = { ...roles.value[0] };
      });
    };
    const sendInvites = async () => {
      if (isFormValid()) {
        loading.value = true;
        resetInvitations.value();
        for (let i = 0; i < invitations.value.length; i++) {
          const invite = invitations.value[i];
          if (invite && invite.emailAddress) {
            const existingInvitation = pendingOrgInvitations.value.find(
              (pendingInvitation) =>
                pendingInvitation.recipientEmail.toLowerCase() ===
                invite.emailAddress.toLowerCase()
            );
            if (existingInvitation) {
              await resendInvitation.value(existingInvitation);
            } else {
              await createInvitation.value({
                recipientEmail: invite.emailAddress,
                sentDate: new Date(),
                membership: [
                  {
                    membershipType: invite.selectedRole.name.toUpperCase(),
                    orgId: currentOrganization.id,
                  },
                ],
              });
            }
          }
        }
        resetForm();
        ctx.emit("invites-complete");
        loading.value = false;
      }
    };
    const cancel = () => {
      resetForm();
    };
    (() => {
      roles.value = roleInfos.value;
      for (let i = 0; i < 3; i++) {
        invitations.value.push({
          emailAddress: "",
          role: roles.value[0],
          selectedRole: { ...roles.value[0] },
        });
      }
    })();
    return {
      pendingOrgInvitations,
      roleInfos,
      createInvitation,
      resendInvitation,
      orgStore,
      loading,
      pendingOrgInvitations,
      resetInvitations,
      createInvitation,
      resendInvitation,
      roleInfos,
      $refs,
      invitations,
      emailRules,
      roles,
      availableRoles,
      getIndexedTag,
      hasDuplicates,
      isFormValid,
      removeEmail,
      addEmail,
      resetForm,
      sendInvites,
      cancel,
    };
  },
});
