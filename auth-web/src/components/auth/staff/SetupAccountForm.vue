<template>
  <div>
    <div>
      <v-form ref="directorSearchForm">
        <v-alert type="error" v-show="errorMessage">{{errorMessage}}</v-alert>

        <v-row>
            <v-col class="d-flex" cols="12" xl="6">
                <v-text-field
                filled
                label="Account Name"
                v-model.trim="accountName"
                :rules="accountNameRules"
                persistent-hint
                :disabled="saving"
                />
            </v-col>
            <v-col class="d-flex" cols="12" xl="6">
                <v-select
                :items="accountTypes"
                filled
                item-text="desc"
                item-value="code"
                label="Account Type"
                v-model="accountType"
                />
            </v-col>
            <v-col cols="12" xl="12">
                <v-label>
                    <h4>Products</h4>
                </v-label>
                <v-treeview
                selectable
                open-all
                return-object
                :items="products"
                :item-text="'desc'"
                :item-key="'code'"
                :item-children="'subProducts'"
                v-model="selectedProducts"
                :disabled="saving"
                ></v-treeview>
            </v-col>
            <v-col class="d-flex" cols="12" xl="6">
                <v-text-field
                filled
                label="Email"
                v-model.trim="email"
                :rules="emailRules"
                persistent-hint
                :disabled="saving"
                />
            </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="form__btns pb-0">
            <v-btn
              large
              color="primary"
              class="mr-2 submit-form-btn"
              :loading="saving"
              :disabled="!isFormValid() || saving"
              @click="save"
              data-test="save-button"
            >Submit</v-btn>
            <v-btn
              large
              depressed
              class="cancel-btn"
              color="default"
              :disable="saving"
              @click="cancel"
              data-test="cancel-button"
            >Cancel</v-btn>
          </v-col>
        </v-row>
      </v-form>
    </div>
  </div>
</template>

<script lang="ts">
import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { CreateRequestBody as InvitationRequestBody } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import StaffModule from '@/store/modules/staff'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('staff', ['products', 'accountTypes'])
  },
  methods: {
    ...mapActions('org', ['createOrg', 'addOrgProducts', 'syncOrganization', 'createInvitation']),
    ...mapActions('staff', ['getProducts', 'getAccountTypes'])
  }
})
export default class SetupAccountForm extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private staffStore = getModule(StaffModule, this.$store)
  private accountName: string = ''
  private accountType: string = ''
  private errorMessage: string = ''
  private saving = false
  private selectedProducts: ProductCode[] = []
  private email = ''
  private readonly createOrg!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>
  private readonly addOrgProducts!: (productsRequestBody: ProductsRequestBody) => Promise<Products>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly getProducts!: () => Promise<ProductCode[]>
  private readonly getAccountTypes!: () => Promise<AccountType[]>
  private readonly createInvitation!: (Invitation) => Promise<void>
  private readonly products!: ProductCode[]
  private readonly accountTypes!: AccountType[]

  $refs: {
    directorSearchForm: HTMLFormElement
  }

  private readonly accountNameRules = [
    v => !!v || 'An account name is required'
  ]

  private readonly emailRules = [
    v => !!v || 'An email is required',
    v => /.+@.+\..+/.test(v) || 'email must be valid'
  ]

  private isFormValid (): boolean {
    return !!this.accountName &&
      this.selectedProducts.length &&
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
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      const createRequestBody: CreateRequestBody = {
        name: this.accountName,
        typeCode: this.accountType
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
        const organization = await this.createOrg(createRequestBody)
        await this.syncOrganization(organization.id)
        await this.addOrgProducts(addProductsRequestBody)
        await this.createInvitation({
          recipientEmail: this.email,
          sentDate: new Date(),
          membership: [{ membershipType: 'ADMIN', orgId: organization.id }]
        })
        this.$store.commit('updateHeader')
        this.saving = false
        // TODO: Redirect/Show success message once the proper design comes
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
              'An error occurred while attempting to create your account.'
        }
      }
    }
  }

  private cancel () {
    this.$router.push({ path: '/home' })
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
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
