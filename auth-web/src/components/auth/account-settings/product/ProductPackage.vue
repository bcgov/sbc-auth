<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Product Packges
      </h2>
      <p class="mt-3 payment-page-sub">
        Select multiple additional products this account require access. By default the account will have
        access to adipiscing elit. Aliquam at porttitor sem.  Aliquam erat volutpat. Donec placerat.
      </p>
      <h4 class="mt-3 payment-page-sub">Select Additional Product(s)</h4>
    </div>
    <SingleProduct
      :productDetails="productDetails"
      @set-selected-product="setSelectedProduct"
      :userName="currentUser.fullName"
      :orgName="currentOrganization.name"
    ></SingleProduct>
    <SingleProduct
      :productDetails="productDetails"
      @set-selected-product="setSelectedProduct"
    ></SingleProduct>

        <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          @click="closeError"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins, Vue } from 'vue-property-decorator'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Organization } from '@/models/Organization'
import SingleProduct from '@/components/auth/common/SingleProduct.vue'
import { namespace } from 'vuex-class'
import { productStatus } from '@/util/constants'

const OrgModule = namespace('org')
const userModule = namespace('user')

@Component({
  components: {
    SingleProduct,
    ModalDialog
  }
})
export default class ProductPackage extends Mixins(AccountChangeMixin) {
  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @userModule.State('currentUser') public currentUser!: KCUserProfile

  public isBtnSaved = false
  public disableSaveBtn = false
  public isLoading: boolean = false
  public errorTitle = 'Payment Update Failed'
  public errorText = ''

  $refs: {
      errorDialog: ModalDialog
  }

  public productDetails: any = {
    title: 'Wills Registry',
    subtitle: 'Registration and search for wills',
    status: productStatus.REQUEST
  }

  public setSelectedProduct (product) {
    // set product and save call come here
    // eslint-disable-next-line no-console
    console.log('selectedproduct', product)
    // open when error
    // this.$refs.errorDialog.open()
  }

  private async mounted () {
    // make call to get all products here
  }
  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}

.save-btn.disabled {
  pointer-events: none;
}
</style>
