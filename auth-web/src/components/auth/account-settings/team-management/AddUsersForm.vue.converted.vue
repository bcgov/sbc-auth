import { defineComponent, computed, ref } from "@vue/composition-api";
import {
  AddUserBody,
  AddUsersToOrgBody,
  Member,
  MembershipType,
  Organization,
  RoleInfo,
} from "@/models/Organization";
import { Component, Emit, Vue } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { Invitation } from "@/models/Invitation";
import OrgModule from "@/store/modules/org";
import PasswordRequirementAlert from "@/components/auth/common/PasswordRequirementAlert.vue";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    PasswordRequirementAlert,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const roleInfos = computed(() => ctx.root.$store.state.user.roleInfos);
    const createUsers = () => ctx.root.$store.dispatch("org/createUsers");
    const loading = ref(false);
    const currentOrganization = ref<Organization>(undefined);
    const currentMembership = ref<Member>(undefined);
    const createUsers = ref<(AddUsersToOrgBody) => Promise<void>>(undefined);
    const inputHints = ref({
      username: "Minimum 8 characters",
      password: "See requirements above",
    });
    const $refs = ref<{
      form: HTMLFormElement;
    }>(undefined);
    const users = ref<AddUserBody[]>([]);
    const roleInfos = ref<RoleInfo[]>(undefined);
    const userNameRules = ref([
      (value) => validateUserName(value) || inputHints.value.username,
    ]);
    const passwordRules = ref([
      (value) => CommonUtils.validatePasswordRules(value) || `Invalid Password`,
    ]);
    const availableRoles = computed(() => {
      if (currentMembership.value.membershipTypeCode !== MembershipType.Admin) {
        return roleInfos.value.filter((role) => role.name !== "Admin");
      }
      return roleInfos.value;
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const getDefaultRow = (): AddUserBody => {
      return {
        username: "",
        password: "",
        selectedRole: { ...roleInfos.value[0] },
        membershipType: roleInfos.value[0].name,
      };
    };
    const validateUserName = (value) => {
      return value?.trim().length >= 8;
    };
    const hasDuplicates = (): boolean => {
      const users = users.value.filter((user) => user.username);
      return (
        new Set(users.map((user) => user.username.toLowerCase())).size !==
        users.length
      );
    };
    const isFormValid = (): boolean => {
      let isValid: boolean = false;
      for (let user of users.value) {
        if (user.username && user.password) {
          isValid =
            CommonUtils.validatePasswordRules(user.password) &&
            validateUserName(user.username);
          if (!isValid) break;
        }
      }
      return isValid && !hasDuplicates();
    };
    const removeUser = (index: number) => {
      users.value.splice(index, 1);
    };
    const addUser = () => {
      users.value.push(getDefaultRow());
    };
    const resetForm = () => {
      ctx.refs.form?.reset();
      ctx.root.$nextTick(() => {
        users.value = [];
        for (let i = 0; i < 3; i++) {
          users.value.push(getDefaultRow());
        }
      });
    };
    const addUsers = async () => {
      if (isFormValid()) {
        loading.value = true;
        for (let i = users.value.length - 1; i >= 0; i--) {
          const user = users.value[i];
          if (!user.username.trim() && !user.password.trim()) {
            users.value.splice(i, 1);
          } else {
            user.membershipType = user?.selectedRole?.name?.toUpperCase();
            user.username = user.username.toLowerCase();
          }
        }
        await createUsers.value({
          orgId: currentOrganization.value.id,
          users: users.value,
        });
        resetForm();
        addUsersComplete();
        loading.value = false;
      }
    };
    const addUsersComplete = () => {
      loading.value = false;
    };
    const cancel = () => {
      resetForm();
    };
    (() => {
      resetForm();
    })();
    return {
      currentOrganization,
      currentMembership,
      roleInfos,
      createUsers,
      loading,
      currentOrganization,
      currentMembership,
      createUsers,
      inputHints,
      $refs,
      users,
      roleInfos,
      userNameRules,
      passwordRules,
      availableRoles,
      getIndexedTag,
      getDefaultRow,
      validateUserName,
      hasDuplicates,
      isFormValid,
      removeUser,
      addUser,
      resetForm,
      addUsers,
      addUsersComplete,
      cancel,
    };
  },
});
