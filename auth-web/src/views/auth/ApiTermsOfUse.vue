<template>
  <v-container class="center-container">
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <router-link :to="developerAccessUrl">
          <v-icon
            small
            color="primary"
            class="mr-1"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back to Developer Access</span>
        </router-link>
      </div>
    </nav>

    <v-alert
      outlined
      color="primary"
      icon="mdi-information-outline"
      class="api-terms-alert mb-6"
      data-test="api-terms-alert"
    >
      <strong>Important:</strong> You have not yet accepted the latest API Terms of Use.
      Please review the Terms of Use before you continue.
    </v-alert>

    <v-alert
      v-if="loadErrorMessage"
      outlined
      color="error"
      icon="mdi-alert"
      class="api-terms-error-alert mb-6"
      data-test="api-terms-load-error"
    >
      <strong>Error:</strong> {{ loadErrorMessage }}
    </v-alert>

    <v-alert
      v-if="acceptErrorMessage"
      outlined
      color="error"
      icon="mdi-alert"
      class="api-terms-error-alert mb-6"
      data-test="api-terms-accept-error"
    >
      <strong>Error:</strong> {{ acceptErrorMessage }}
    </v-alert>

    <v-card
      v-if="!loadErrorMessage"
      class="py-4 px-4"
      data-test="api-terms-card"
    >
      <v-card-title class="flex-column align-center">
        <h1 class="view-header__title text-center">
          API Terms of Use for all products
        </h1>
      </v-card-title>
      <v-card-text>
        <div
          v-if="isLoading"
          class="text-center py-8"
        >
          <v-progress-circular
            indeterminate
            color="primary"
            data-test="api-terms-loading"
          />
        </div>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div
          v-else
          data-test="api-terms-content"
          v-html="termsContent"
        />
      </v-card-text>
      <v-divider class="mt-3" />
      <v-card-actions class="pt-6 px-4">
        <v-spacer />
        <v-btn
          large
          outlined
          depressed
          color="primary"
          class="px-7 mr-2"
          :to="developerAccessUrl"
          data-test="decline-api-terms-button"
        >
          Decline
        </v-btn>
        <v-btn
          large
          color="primary"
          class="font-weight-bold px-8"
          data-test="accept-api-terms-button"
          :disabled="isLoading"
          :loading="isAccepting"
          @click="accept()"
        >
          Agree
        </v-btn>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import DocumentService from '@/services/document.services'
import { useOrgStore } from '@/stores/org'

const API_TERMS_DOCUMENT_TYPE = 'termsofuse_api'
const TERMS_LOAD_FAILED_MESSAGE = 'We were not able to load the terms of use. Please refresh the page or try again later.'
const TERMS_VERSION_MISMATCH_MESSAGE = 'The API Terms of Use have been updated. Please refresh the page to review the latest version.'
const TERMS_ACCEPT_FAILED_MESSAGE = 'The API Terms of Use could not be accepted. Please try again.'

export default defineComponent({
  name: 'ApiTermsOfUse',
  props: {
    orgId: {
      type: [String, Number],
      required: true
    }
  },
  setup (props, { root }) {
    const orgStore = useOrgStore()
    const state = reactive({
      isLoading: true,
      isAccepting: false,
      loadErrorMessage: '',
      termsContent: '',
      termsVersionId: '',
      acceptErrorMessage: ''
    })

    const developerAccessUrl = computed(() => `/account/${props.orgId}/settings/developer-access`)

    const loadTerms = async () => {
      try {
        const response = await DocumentService.getTermsOfService(API_TERMS_DOCUMENT_TYPE)
        state.termsContent = response?.data?.content || ''
        state.termsVersionId = response?.data?.versionId || ''
        if (!state.termsVersionId) {
          state.loadErrorMessage = TERMS_LOAD_FAILED_MESSAGE
        }
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e)
        state.loadErrorMessage = TERMS_LOAD_FAILED_MESSAGE
      }
    }

    onMounted(async () => {
      await loadTerms()
      state.isLoading = false
    })

    const accept = async () => {
      state.isAccepting = true
      state.acceptErrorMessage = ''
      try {
        await orgStore.acceptApiTerms(Number(props.orgId), state.termsVersionId)
        // named route navigation so 'openCreateKey' is passed as a param (not shown in the URL) instead of a query string
        root.$router.push({ name: 'developer-access', params: { orgId: String(props.orgId), openCreateKey: 'true' } })
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e)
        state.acceptErrorMessage = e?.response?.data?.code === 'API_TERMS_VERSION_MISMATCH'
          ? TERMS_VERSION_MISMATCH_MESSAGE
          : TERMS_ACCEPT_FAILED_MESSAGE
      } finally {
        state.isAccepting = false
      }
    }

    return {
      ...toRefs(state),
      developerAccessUrl,
      accept
    }
  }
})
</script>

<style lang="scss" scoped>
.crumbs a {
  font-size: 0.875rem;
  text-decoration: none;

  i {
    margin-top: -2px;
  }
}

.crumbs a:hover {
  span {
    text-decoration: underline;
  }
}

.api-terms-alert {
  background-color: #fff !important;
  font-size: 14px;

  ::v-deep .v-alert__content {
    color: rgba(0, 0, 0, 0.87);
  }
}

.api-terms-error-alert {
  background-color: #f9e7e7 !important;
  font-size: 14px;

  ::v-deep .v-alert__content {
    color: rgba(0, 0, 0, 0.87);
  }
}

</style>
