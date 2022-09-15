import {
  defineComponent,
  computed,
  toRefs,
  ref,
  watch,
  PropType,
} from "@vue/composition-api";
import {
  AffiliationTypes,
  BusinessState,
  CorpType,
  FilingTypes,
  LDFlags,
  LegalTypes,
  NrDisplayStates,
  NrEntityType,
  NrState,
  NrTargetTypes,
  SessionStorageKeys,
} from "@/util/constants";
import {
  Business,
  BusinessRequest,
  NameRequest,
  Names,
} from "@/models/business";
import { Component, Emit, Mixins, Prop, Watch } from "vue-property-decorator";
import {
  CorpTypeCd,
  GetCorpFullDescription,
} from "@bcrs-shared-components/corp-type-module";
import { Organization, RemoveBusinessPayload } from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import ConfigHelper from "@/util/config-helper";
import DateMixin from "@/components/auth/mixins/DateMixin.vue";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import { appendAccountId } from "sbc-common-components/src/util/common-util";
export default defineComponent({
  props: {
    selectedColumns: { default: [], type: Object as PropType<Array<string>> },
    loading: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const businesses = computed(
      () => ctx.root.$store.state.business.businesses
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const createNamedBusiness = () =>
      ctx.root.$store.dispatch("business/createNamedBusiness");
    const { selectedColumns, loading } = toRefs(props);
    const businesses = ref<Business[]>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const createNamedBusiness =
      ref<(filingBody: BusinessRequest, nrNumber: string) => Promise<any>>(
        undefined
      );
    const headers = ref<Array<any>>([]);
    const isLoading = ref<boolean>(false);
    const dropdown = ref<Array<boolean>>([]);
    const showCol = ref((col): boolean => {
      return selectedColumns.value.includes(col);
    });
    const entityCount = computed((): number => {
      return businesses.value.length;
    });
    const getHeaders = computed((): Array<any> => {
      return headers.value?.filter((x) => x.show);
    });
    const getMaxHeight = computed((): string => {
      return entityCount.value > 5 ? "32rem" : null;
    });
    const isNameRequest = (corpType: string): boolean => {
      return corpType === CorpType.NAME_REQUEST;
    };
    const isTemporaryBusinessRegistration = (corpType: string): boolean => {
      return (
        corpType === CorpType.NEW_BUSINESS ||
        corpType === CorpType.NEW_REGISTRATION
      );
    };
    const isNumberedIncorporationApplication = (item: Business): boolean => {
      return (
        item.corpType.code === CorpType.NEW_BUSINESS &&
        item.name === item.businessIdentifier
      );
    };
    const canUseNameRequest = (business: Business): boolean => {
      const supportedEntityFlags =
        LaunchDarklyService.getFlag(LDFlags.IaSupportedEntities)?.split(" ") ||
        [];
      return (
        isNameRequest(business.corpType.code) &&
        business.nameRequest?.enableIncorporation &&
        supportedEntityFlags.includes(business.nameRequest?.legalType)
      );
    };
    const name = (item: Business): string => {
      return isNumberedIncorporationApplication(item)
        ? "Numbered Benefit Company"
        : item.name;
    };
    const isApprovedName = (name: Names): boolean => {
      return name.state === NrState.APPROVED;
    };
    const isRejectedName = (name: Names): boolean => {
      return name.state === NrState.REJECTED;
    };
    const number = (item: Business): string => {
      switch (true) {
        case isNumberedIncorporationApplication(item):
          return "Pending";
        case isTemporaryBusinessRegistration(item.corpType.code):
          return item.nrNumber;
        case isNameRequest(item.corpType.code):
          return item.nameRequest?.nrNumber;
        default:
          return item.businessIdentifier;
      }
    };
    const type = (item: Business): string => {
      switch (true) {
        case isNameRequest(item.corpType.code):
          return AffiliationTypes.NAME_REQUEST;
        case isTemporaryBusinessRegistration(item.corpType.code):
          return tempDescription(item.corpType.code as CorpType);
        default:
          return typeDescription(item.corpType.code as CorpTypeCd);
      }
    };
    const tempDescription = (corpType: CorpType): string => {
      switch (corpType) {
        case CorpType.NEW_BUSINESS:
          return AffiliationTypes.INCORPORATION_APPLICATION;
        case CorpType.NEW_REGISTRATION:
          return AffiliationTypes.REGISTRATION;
      }
    };
    const typeDescription = (corpType: CorpTypeCd): string => {
      return GetCorpFullDescription(corpType);
    };
    const status = (item: Business): string => {
      switch (true) {
        case isNameRequest(item.corpType.code) && !!item.nameRequest:
          return NrDisplayStates[NrState[item.nameRequest.state]];
        case isTemporaryBusinessRegistration(item.corpType.code):
          return BusinessState.DRAFT;
        case !!item.status:
          return item.status.toLowerCase();
        default:
          return BusinessState.ACTIVE;
      }
    };
    const folio = (item: Business): string => {
      return item.nameRequest && (item.nameRequest.folioNumber || "");
    };
    const lastModified = (item: Business): string => {
      switch (true) {
        case !!item.lastModified:
          return dateToPacificDate(new Date(item.lastModified));
        case !!item.modified:
          return dateToPacificDate(new Date(item.modified));
        default:
          return ctx.root.$t("notAvailable").toString();
      }
    };
    const modifiedBy = (item: Business): string => {
      if (item.modifiedBy === "None None" || !item.modifiedBy) {
        return ctx.root.$t("notAvailable").toString();
      } else {
        return item.modifiedBy || ctx.root.$t("notAvailable").toString();
      }
    };
    const open = (item: Business): void => {
      if (item.corpType.code === CorpType.NAME_REQUEST) {
        goToNameRequest(item.nameRequest);
      } else {
        goToDashboard(item.businessIdentifier);
      }
    };
    const useNameRequest = async (item: Business) => {
      switch (item.nameRequest.target) {
        case NrTargetTypes.LEAR:
          let businessIdentifier = item.businessIdentifier;
          if (item.corpType.code === CorpType.NAME_REQUEST) {
            isLoading.value = true;
            businessIdentifier = await createBusinessRecord(item);
            isLoading.value = false;
          }
          goToDashboard(businessIdentifier);
          break;
        case NrTargetTypes.ONESTOP:
          goToOneStop();
          break;
        case NrTargetTypes.COLIN:
          goToCorpOnline();
          break;
      }
    };
    const goToDashboard = (businessIdentifier: string): void => {
      ConfigHelper.addToSession(
        SessionStorageKeys.BusinessIdentifierKey,
        businessIdentifier
      );
      let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`;
      window.location.href = appendAccountId(decodeURIComponent(redirectURL));
    };
    const goToNameRequest = (nameRequest: NameRequest): void => {
      ConfigHelper.setNrCredentials(nameRequest);
      window.location.href = appendAccountId(
        `${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`
      );
    };
    const goToOneStop = (): void => {
      window.location.href = appendAccountId(ConfigHelper.getOneStopUrl());
    };
    const goToCorpOnline = (): void => {
      window.location.href = appendAccountId(
        ConfigHelper.getCorporateOnlineUrl()
      );
    };
    const createBusinessRecord = async (
      business: Business
    ): Promise<string> => {
      let filingResponse = null;
      if (
        [LegalTypes.SP, LegalTypes.GP].includes(
          business.nameRequest?.legalType as LegalTypes
        )
      ) {
        filingResponse = await createBusinessRegistration(business);
      } else {
        filingResponse = await createBusinessIA(business);
      }
      if (filingResponse?.errorMsg) {
        ctx.emit("add-unknown-error");
        return "";
      } else {
        return filingResponse.data.filing.business.identifier;
      }
    };
    const createBusinessIA = async (business: Business): Promise<any> => {
      const filingBody: BusinessRequest = {
        filing: {
          header: {
            name: FilingTypes.INCORPORATION_APPLICATION,
            accountId: currentOrganization.value.id,
          },
          business: {
            legalType: business.nameRequest.legalType,
          },
          incorporationApplication: {
            nameRequest: {
              legalType: business.nameRequest.legalType,
              nrNumber: business.businessIdentifier,
            },
          },
        },
      };
      return createNamedBusiness.value(filingBody, business.businessIdentifier);
    };
    const createBusinessRegistration = async (
      business: Business
    ): Promise<any> => {
      const filingBody: BusinessRequest = {
        filing: {
          header: {
            name: FilingTypes.REGISTRATION,
            accountId: currentOrganization.value.id,
          },
          registration: {
            nameRequest: {
              legalType: business.nameRequest.legalType,
              nrNumber: business.businessIdentifier,
            },
            business: {
              natureOfBusiness: business.nameRequest.natureOfBusiness,
            },
          },
        },
      };
      if (business.nameRequest.legalType === LegalTypes.SP) {
        if (business.nameRequest.entityTypeCd === NrEntityType.FR) {
          filingBody.filing.registration.businessType = "SP";
        } else if (business.nameRequest.entityTypeCd === NrEntityType.DBA) {
          filingBody.filing.registration.businessType = "DBA";
        }
      }
      return createNamedBusiness.value(filingBody, business.businessIdentifier);
    };
    const customSort = (items, index, isDesc): any => {
      items.sort((a, b) => {
        switch (index[0]) {
          case "lastModified":
            let dateA, dateB;
            if (a.lastModified) {
              dateA = a.lastModified;
            } else {
              dateA = a.modified;
            }
            if (b.lastModified) {
              dateB = b.lastModified;
            } else {
              dateB = b.modified;
            }
            if (!isDesc[0]) {
              return +new Date(dateB) - +new Date(dateA);
            } else {
              return +new Date(dateA) - +new Date(dateB);
            }
          case "name":
            let nameA, nameB;
            if (a.nameRequest) {
              nameA = a.nameRequest?.names[0].name;
            } else {
              nameA = isNumberedIncorporationApplication(a)
                ? "Numbered Benefit Company"
                : a.name;
            }
            if (b.nameRequest) {
              nameB = b.nameRequest?.names[0].name;
            } else {
              nameB = isNumberedIncorporationApplication(b)
                ? "Numbered Benefit Company"
                : b.name;
            }
            if (!isDesc[0]) {
              return nameA.toLowerCase().localeCompare(nameB.toLowerCase());
            } else {
              return nameB.toLowerCase().localeCompare(nameA.toLowerCase());
            }
          case "number":
            if (!isDesc[0]) {
              return number(a)
                .toLowerCase()
                .localeCompare(number(b).toLowerCase());
            } else {
              return number(b)
                .toLowerCase()
                .localeCompare(number(a).toLowerCase());
            }
          case "type":
            if (!isDesc[0]) {
              return type(a).toLowerCase().localeCompare(type(b).toLowerCase());
            } else {
              return type(b).toLowerCase().localeCompare(type(a).toLowerCase());
            }
          case "status":
            if (!isDesc[0]) {
              return status(a)
                .toLowerCase()
                .localeCompare(status(b).toLowerCase());
            } else {
              return status(b)
                .toLowerCase()
                .localeCompare(status(a).toLowerCase());
            }
          case "modifiedBy":
            if (!isDesc[0]) {
              return modifiedBy(a)
                .toLowerCase()
                .localeCompare(modifiedBy(b).toLowerCase());
            } else {
              return modifiedBy(b)
                .toLowerCase()
                .localeCompare(modifiedBy(a).toLowerCase());
            }
        }
      });
      return items;
    };
    const removeBusiness = (business: Business): RemoveBusinessPayload => {
      return {
        orgIdentifier: currentOrganization.value.id,
        business,
      };
    };
    const applyHeaders = (): void => {
      headers.value = [
        {
          text: "Business Name",
          align: "start",
          value: "name",
          sortable: true,
          show: true,
        },
        {
          text: "Number",
          value: "number",
          sortable: true,
          show: showCol.value("Number"),
        },
        {
          text: "Type",
          value: "type",
          sortable: true,
          show: showCol.value("Type"),
        },
        {
          text: "Status",
          value: "status",
          sortable: true,
          show: showCol.value("Status"),
        },
        {
          text: "Folio",
          value: "folio",
          sortable: false,
          show: showCol.value("Folio"),
        },
        {
          text: "Last Modified",
          value: "lastModified",
          sortable: true,
          show: showCol.value("Last Modified"),
        },
        {
          text: "Modified By",
          value: "modifiedBy",
          sortable: true,
          show: showCol.value("Modified By"),
        },
        {
          text: "Actions",
          align: "end",
          value: "action",
          sortable: false,
          show: true,
        },
      ];
    };
    watch(selectedColumns, applyHeaders, { immediate: true });
    return {
      businesses,
      currentOrganization,
      createNamedBusiness,
      businesses,
      currentOrganization,
      createNamedBusiness,
      headers,
      isLoading,
      dropdown,
      showCol,
      entityCount,
      getHeaders,
      getMaxHeight,
      isNameRequest,
      isTemporaryBusinessRegistration,
      isNumberedIncorporationApplication,
      canUseNameRequest,
      name,
      isApprovedName,
      isRejectedName,
      number,
      type,
      tempDescription,
      typeDescription,
      status,
      folio,
      lastModified,
      modifiedBy,
      open,
      useNameRequest,
      goToDashboard,
      goToNameRequest,
      goToOneStop,
      goToCorpOnline,
      createBusinessRecord,
      createBusinessIA,
      createBusinessRegistration,
      customSort,
      removeBusiness,
      applyHeaders,
    };
  },
});
