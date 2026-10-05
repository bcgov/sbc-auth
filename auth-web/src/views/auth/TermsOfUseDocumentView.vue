<template>
  <v-container class="center-container">
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <router-link :to="accountInfoUrl">
          <v-icon
            small
            color="primary"
            class="mr-1"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back to Account</span>
        </router-link>
      </div>
    </nav>
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        {{ terms.title || $t(isGovmUser ? 'govm_tos_title' : 'tos_title') }}
      </h1>
    </div>

    <v-alert
      v-if="loadErrorMessage"
      text
      outlined
      color="error"
      icon="mdi-alert"
      class="mt-5"
      type="error"
      data-test="terms-load-error"
    >
      <span class="error-text"><strong>Error:</strong> {{ loadErrorMessage }}</span>
    </v-alert>

    <v-card
      v-else
      class="mt-5 mb-10 py-4 px-4"
    >
      <v-card-text>
        <TermsOfUse
          v-if="!terms.docType"
          @tos-version-updated="false"
        />
        <div
          v-else-if="isLoading"
          class="text-center py-8"
        >
          <v-progress-circular
            indeterminate
            color="primary"
            data-test="terms-loading"
          />
        </div>
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div
          v-else
          data-test="terms-content"
          v-html="termsContent"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import DocumentService from '@/services/document.services'
import { LoginSource } from '@/util/constants'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { storeToRefs } from 'pinia'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const TERMS_LOAD_FAILED_MESSAGE = 'We were not able to load the terms of use. Please refresh the page or try again later.'

const TERMS_TYPES: Record<string, { docType?: string, title?: string }> = {
  account: {}, // no docType so the TermsOfUse component renders default 'termsofuse' doc
  api: { docType: 'termsofuse_api', title: 'API Terms of Use for all products' }
}

export default defineComponent({
  name: 'TermsOfUseDocumentView',
  components: {
    TermsOfUse
  },
  props: {
    termsType: {
      type: String,
      required: true
    }
  },
  setup (props) {
    const { currentOrganization } = storeToRefs(useOrgStore())
    const { currentUser } = storeToRefs(useUserStore())
    const state = reactive({
      isLoading: true,
      loadErrorMessage: '',
      termsContent: ''
    })

    const accountInfoUrl = computed(() => `/account/${currentOrganization.value?.id}/settings`)
    const isGovmUser = computed(() => currentUser.value?.loginSource?.toUpperCase() === LoginSource.IDIR.toUpperCase())
    const terms = computed(() => TERMS_TYPES[props.termsType] || TERMS_TYPES.account)

    const loadTerms = async () => {
      state.loadErrorMessage = ''
      state.termsContent = ''
      const docType = terms.value.docType
      state.isLoading = !!docType
      if (!docType) return
      try {
        const response = await DocumentService.getTermsOfService(docType)
        if (docType !== terms.value.docType) return // return if terms type is switched during the request
        state.termsContent = response?.data?.content || ''
        if (!state.termsContent) {
          state.loadErrorMessage = TERMS_LOAD_FAILED_MESSAGE
        }
      } catch (e) {
        if (docType !== terms.value.docType) return
        // eslint-disable-next-line no-console
        console.error(e)
        state.loadErrorMessage = TERMS_LOAD_FAILED_MESSAGE
      }
      state.isLoading = false
    }

    // load Terms document when termsType (route param) changes
    watch(() => props.termsType, loadTerms, { immediate: true })

    return {
      ...toRefs(state),
      accountInfoUrl,
      isGovmUser,
      terms
    }
  }
})
</script>

<style lang="scss" scoped>
.error-text {
  color: #212529;
  font-size: 14px;
}

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
</style>
