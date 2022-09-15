import { defineComponent, computed, ref } from "@vue/composition-api";
import { AccessType, Account, SessionStorageKeys } from "@/util/constants";
import { AccountSettings } from "@/models/account-settings";
import Component from "vue-class-component";
import ConfigHelper from "@/util/config-helper";
import { Organization } from "@/models/Organization";
import Vue from "vue";
import { mapState } from "vuex";
export default defineComponent({
  name: "AccountMixin",
  props: {},
  setup(_props, ctx) {
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const currentOrganization = ref<Organization>(undefined);
    const isPremiumAccount = computed((): boolean => {
      return currentOrganization.value?.orgType === Account.PREMIUM;
    });
    const isRegularAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.REGULAR;
    });
    const anonAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.ANONYMOUS;
    });
    const isGovmAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.GOVM;
    });
    const isGovnAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.GOVN;
    });
    const getAccountFromSession = (): AccountSettings => {
      return JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || "{}")
      );
    };
    return {
      currentUser,
      currentOrganization,
      currentMembership,
      currentOrganization,
      isPremiumAccount,
      isRegularAccount,
      anonAccount,
      isGovmAccount,
      isGovnAccount,
      getAccountFromSession,
    };
  },
});
