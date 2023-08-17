<template>
  <div>
    <v-form ref="directorSearchForm">
      <!-- Name of Account -->
      <v-row>
        <v-col
          cols="12"
          class="pb-0 mb-2"
        >
          <h4 class="mb-2">
            Enter a name for this account
          </h4>
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          class=""
        >
          <v-text-field
            v-model.trim="accountName"
            filled
            label="Account Name"
            :rules="accountNameRules"
            persistent-hint
            :disabled="saving"
            data-test="account-name"
          />
        </v-col>
      </v-row>
      <!-- Email/Confirm Email -->
      <v-row>
        <v-col
          cols="12"
          class="pb-0"
        >
          <h4 class="mb-2">
            Account Admin Contact
          </h4>
          <p class="mb-6">
            Enter the email address of the user who will be managing this account. An email will be sent to this user to verify and activate this account
          </p>
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          class="pt-0 pb-0"
        >
          <v-text-field
            v-model.trim="email"
            filled
            label="Email Address"
            :rules="emailRules"
            persistent-hint
            :disabled="saving"
            data-test="email-address"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          class="pt-0 pb-0"
        >
          <v-text-field
            v-model.trim="emailConfirm"
            filled
            label="Confirm Email Address"
            :rules="emailRules"
            persistent-hint
            :error-messages="emailMatchError()"
            :disabled="saving"
            data-test="confirm-email-address"
          />
        </v-col>
      </v-row>
      <!-- Select Products -->
      <v-row>
        <v-col
          cols="12"
          class="pb-0"
        >
          <h4 class="mb-2">
            Select Product(s)
          </h4>
          <p class="mb-4">
            Which products will this account have access to?
          </p>
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          class="pt-0 pb-0"
        >
          <v-treeview
            v-model="selectedProducts"
            selectable
            open-all
            return-object
            :items="products"
            :item-text="'desc'"
            :item-key="'code'"
            :item-children="'subProducts'"
            :disabled="saving"
            data-test="product-select"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col
          cols="12"
          class="form__btns pb-0"
        >
          <v-btn
            large
            color="primary"
            class="mr-2 submit-form-btn"
            :loading="saving"
            :disabled="!isFormValid() || saving"
            data-test="save-button"
            @click="save"
          >
            Create Account
          </v-btn>
          <v-btn
            large
            depressed
            class="cancel-btn"
            color="default"
            :disable="saving"
            data-test="cancel-button"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </v-col>
      </v-row>
    </v-form>
    <!-- Error Dialog -->
    <ModalDialog
      ref="errorDialog"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          data-test="dialog-ok-button"
          @click="close()"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { AccessType, Pages } from '@/util/constants'
import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('staff', ['products', 'accountTypes'])
  },
  methods: {
    ...mapActions('org', ['createOrgByStaff', 'addProductsToOrg', 'createInvitation']),
    ...mapActions('staff', ['getProducts', 'getAccountTypes'])
  },
  components: {
    ModalDialog
  }
})
export default class SetupAccountForm extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private staffStore = getModule(StaffModule, this.$store)
  private accountName: string = ''
  private accountType: string = ''
  private errorMessage: string = ''
  private saving = false
  private loader = false
  private selectedProducts: ProductCode[] = []
  private email = ''
  private emailConfirm = ''
  private dialogTitle = ''
  private dialogText = ''
  private readonly createOrgByStaff!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>
  private readonly addProductsToOrg!: (productsRequestBody: ProductsRequestBody) => Promise<Products>
  private readonly getProducts!: () => Promise<ProductCode[]>
  private readonly getAccountTypes!: () => Promise<AccountType[]>
  private readonly createInvitation!: (Invitation) => Promise<void>
  private readonly products!: ProductCode[]
  private readonly accountTypes!: AccountType[]

  $refs: {
    directorSearchForm: HTMLFormElement,
    errorDialog: ModalDialog
  }

  private readonly accountNameRules = [
    v => !!v || 'An account name is required'
  ]

  private readonly emailRules = [
    v => !!v || 'An email address is required',
    v => /.+@.+\..+/.test(v) || 'Invalid Email Address'
  ]

  private emailMatchError () {
    return (this.email === this.emailConfirm) ? null : 'Email Address does not match'
  }

  private isFormValid (): boolean {
    return !!this.accountName &&
      this.selectedProducts.length &&
      !this.emailMatchError() &&
      this.$refs.directorSearchForm.validate()
  }

  async mounted () {
    await this.getProducts()
    await this.getAccountTypes()
    if (this.accountTypes && this.accountTypes.length) {
      const defaultAcc = this.accountTypes.filter((account) => account.default)
      this.accountType = (defaultAcc && defaultAcc.length && defaultAcc[0].code) ? defaultAcc[0].code : this.accountType
    }
  }

  private async save () {
    this.loader = this.saving
    if (this.isFormValid()) {
      const createRequestBody: CreateRequestBody = {
        name: this.accountName,
        typeCode: this.accountType,
        accessType: AccessType.ANONYMOUS
      }
      const productsSelected: Products[] = this.selectedProducts.map((prod) => {
        return {
          productCode: prod.code,
          productRoles: ['search']
        }
      })
      const addProductsRequestBody: ProductsRequestBody = {
        subscriptions: productsSelected
      }
      try {
        this.saving = true
        const organization = await this.createOrgByStaff(createRequestBody)
        await this.addProductsToOrg(addProductsRequestBody)
        await this.createInvitation({
          recipientEmail: this.email,
          sentDate: new Date(),
          membership: [{ membershipType: MembershipType.Admin, orgId: organization.id }]
        })
        this.saving = false
        this.loader = this.saving
        this.$router.push({ path: `/staff-setup-account-success/${AccessType.ANONYMOUS.toLowerCase()}/${this.accountName}` })
      } catch (err) {
        this.saving = false
        switch (err.response.status) {
          case 409:
            this.errorMessage =
              'An account with this name already exists. Try a different account name.'
            break
          case 400:
            if (err.response.data.code === 'MAX_NUMBER_OF_ORGS_LIMIT') {
              this.errorMessage = 'Maximum number of accounts reached'
            } else {
              this.errorMessage = 'Invalid account name'
            }
            break
          default:
            this.errorMessage =
              'Something went wrong while attempting to create this account. Please try again later.'
        }
        this.showEntityNotFoundModal(this.errorMessage)
        this.loader = this.saving
      }
    }
  }

  private cancel () {
    this.$router.push({ path: Pages.STAFF_DASHBOARD })
  }

  showEntityNotFoundModal (msg?) {
    this.dialogTitle = 'An error has occured'
    this.dialogText = msg || 'Something went wrong while attempting to create this account. Please try again later.'
    this.$refs.errorDialog.open()
  }

  close () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}
</style>
