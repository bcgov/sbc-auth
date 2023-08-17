<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2
        class="view-header__title"
        data-test="account-settings-title"
      >
        Authentication
      </h2>
      <v-alert
        class="mt-10"
        icon="mdi-information-outline"
        type="info"
      >
        Changing your authentication method will only affect new users invited to this account. Authentication for administrators and existing users will not be affected.
      </v-alert>
    </div>
    <account-login-option-picker
      @auth-type-selected="setLoginOption"
    />
    <v-divider class="mt-6" />
    <div class="form__btns d-flex">
      <v-btn
        large
        class="save-btn"
        :class="{ disabled: isBtnSaved }"
        :color="isBtnSaved ? 'success' : 'primary'"
        :disabled="disableSaveBtn"
        @click="submit()"
      >
        <v-expand-x-transition>
          <v-icon v-show="isBtnSaved">
            mdi-check
          </v-icon>
        </v-expand-x-transition>
        <span class="save-btn__label">{{ (isBtnSaved) ? 'Saved' : 'Save' }}</span>
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountLoginOptionPicker from '@/components/auth/common/AccountLoginOptionPicker.vue'
import { LoginSource } from '@/util/constants'

@Component({
  components: {
    AccountLoginOptionPicker
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'memberLoginOption'
    ])
  },
  methods: {
    ...mapActions('org', [
      'updateLoginOption'
    ]),
    ...mapMutations('org', ['setMemberLoginOption'])
  }
})
export default class AccountSettingsLoginOption extends Mixins(AccountChangeMixin) {
  private isBtnSaved = false
  private disableSaveBtn = true
  private readonly updateLoginOption!: (loginType:string) => Promise<string>
  private authType = LoginSource.BCSC.toString()

  private errorMessage: string = ''

  setLoginOption (loginType:string) {
    this.authType = loginType
    this.disableSaveBtn = false
    this.isBtnSaved = false
    // this scroll to bottom is needed since the save button can be missed since its out of view port
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'smooth'
    })
  }

  private async submit () {
    this.isBtnSaved = false
    try {
      await this.updateLoginOption(this.authType)
      this.isBtnSaved = true
    } catch (err) {
      this.isBtnSaved = false
      this.disableSaveBtn = false
      // eslint-disable-next-line no-console
      console.error('Error', err)
    }
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

.change-account-link {
  font-size: 0.875rem;
}
</style>
