<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        lg="8"
        class="text-center"
      >
        <v-icon
          size="48"
          color="error"
          class="mb-6"
        >
          mdi-lock-outline
        </v-icon>
        <h1>{{ $t('restrictedAccess') }}</h1>
        <p class="mt-8">
          This account does not have permission to access to the {{ productName }}.
        </p>
        <p class="mb-10">
          Go to Account Setting -> Product Package page to request access.
        </p>
        <div>
          <v-btn
            large
            link
            color="primary"
            class="btn-request-access"
            :to="productUrl"
          >
            Request Access
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'RestrictedProductView',
  props: {
    orgId: {
      type: String,
      default: ''
    },
    productName: {
      type: String,
      default: 'Wills Registry application'
    }
  },
  setup (props) {
    const productUrl = computed<string>(() => {
      return `/account/${props.orgId}/settings/product-settings`
    })

    return { productUrl }
  }
})
</script>
