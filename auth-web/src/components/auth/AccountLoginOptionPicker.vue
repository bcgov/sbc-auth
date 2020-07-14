<template>
  <v-container class="view-container">
    <div>
      <v-row>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card
            flat
            outlined
            hover
            class="account-card text-center px-10 pt-9 pb-12 elevation-2 d-flex"
            @click="selectAuthType(loginSourceEnum.BCSC)"
            :class="{ active: authType == loginSourceEnum.BCSC }"
          >
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-6">
                <v-icon>mdi-account-circle-outline</v-icon>
              </div>
              <div class="account-type__title mb-6">
                BC Services Card
              </div>
              <div class="account-type__details mb-6">
                Use your BC Services Card with a mobile app or a USB card reader
                to verify your identity.
              </div>
              <div>
                <a
                  href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card"
                  target="_blank"
                  >Learn more about the BC Services card</a
                >
              </div>
              <div class="mt-9 mb-2">
                <v-btn
                  large
                  depressed
                  block
                  color="primary"
                  class="font-weight-bold"
                  :outlined="authType != loginSourceEnum.BCSC"
                >
                  {{ authType == loginSourceEnum.BCSC ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card
            flat
            outlined
            hover
            class="account-card text-center px-10 pt-9 pb-12 elevation-2 d-flex"
            @click="selectAuthType(loginSourceEnum.BCEID)"
            :class="{ active: authType == loginSourceEnum.BCEID}"
          >
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-6">
                <v-icon>mdi-two-factor-authentication</v-icon>
              </div>
              <div class="account-type__title mb-6">
                BCeID and 2-factor authentication app
              </div>
              <div class="account-type__details mb-6">
                Login with a BCeID combined with a verification code in a mobile
                app, such as Google or Microsoft Authenticator.
              </div>
              <!-- State Button (Create Account) -->
              <div class="mt-9 mb-2">
                <v-btn
                  large
                  depressed
                  block
                  color="primary"
                  class="font-weight-bold"
                  :outlined="authType != loginSourceEnum.BCEID"
                >
                  {{ authType == loginSourceEnum.BCEID ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Mixins } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { LoginSource } from '@/util/constants'
import { Organization } from '@/models/Organization'

@Component({
  components: {
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'memberLoginOption'
    ])
  },
  methods: {
    ...mapActions('org', [
      'syncMemberLoginOption',
      'updateLoginOption'
    ]),
    ...mapMutations('org', ['setMemberLoginOption'])
  }
})
export default class AccountLoginOptionPicker extends Mixins(AccountChangeMixin, AccountMixin) {
  private btnLabel = 'Save'
  private readonly memberLoginOption!: string
  private readonly syncMemberLoginOption!: (currentAccount: number) => string
  protected readonly syncOrganization!: (
    currentAccount: number
  ) => Promise<Organization>
  private readonly updateLoginOption!: (loginType:string) => Promise<string>

  private errorMessage: string = ''

  private authType = LoginSource.BCSC.toString()

  @Emit('auth-type-selected')
  private selectAuthType (type:string) {
    this.authType = type
    return type
  }

  private get loginSourceEnum () {
    return LoginSource
  }

  private async mounted () {
    if (!this.memberLoginOption) {
      await this.syncMemberLoginOption(this.getAccountFromSession().id)
    }
    this.authType = this.memberLoginOption ? this.memberLoginOption : this.authType
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.v-application p {
  margin-bottom: 3rem;
}

.nv-list {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.nv-list-item {
  vertical-align: top;

  .name,
  .value {
    display: inline-block;
    vertical-align: top;
  }

  .name {
    min-width: 10rem;
    font-weight: 700;
  }
}

.v-list--dense .v-list-item .v-list-item__title {
  font-weight: 700;
}

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

.account-nav-container {
  height: 100%;
  border-right: 1px solid #eeeeee;
}

.header-container {
  display: flex;
  flex-direction: row;
}

// BC Online Account Information
.bcol-acc__name {
  font-size: 1.125rem;
  font-weight: 700;
}

.bcol-acc__meta {
  margin: 0;
  padding: 0;
  list-style-type: none;

  li {
    position: relative;
    display: inline-block;
  }

  li + li {
    &:before {
      content: ' | ';
      display: inline-block;
      position: relative;
      top: -2px;
      left: 2px;
      width: 2rem;
      vertical-align: top;
      text-align: center;
    }
  }
}

.save-btn.disabled {
  pointer-events: none;
}

.save-btn__label {
  padding-left: 0.2rem;
  padding-right: 0.2rem;
}

.change-account-link {
  font-size: 0.875rem;
}
</style>
