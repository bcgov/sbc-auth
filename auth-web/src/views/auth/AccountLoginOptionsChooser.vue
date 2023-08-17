<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Choose authentication for your team
      </h1>
      <p class="mt-3 mb-0">
        There are two different ways that your team can log in. Review the options below to learn more and make
        a selection for your team. You will be able to access authentication methods for your team in your
        <a
          class="text-decoration-underline"
          @click="goToAccountSettings"
        >account settings.</a>
      </p>
    </div>
    <account-login-option-picker @auth-type-selected="setLoginOption" />
    <div class="d-flex mt-10 justify-center">
      <v-btn
        large
        color="primary"
        class="font-weight-bold"
        :disabled="authType == ''"
        @click="submit()"
      >
        Add Team Members
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { LoginSource, Pages } from '@/util/constants'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountLoginOptionPicker from '@/components/auth/common/AccountLoginOptionPicker.vue'
import { Organization } from '@/models/Organization'

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
export default class AccountLoginOptionsChooser extends Mixins(AccountChangeMixin) {
  private btnLabel = 'Save'
  private readonly updateLoginOption!: (loginType:string) => Promise<string>
  private authType = LoginSource.BCSC.toString()
  private readonly currentOrganization!: Organization

  private errorMessage: string = ''

  setLoginOption (loginType:string) {
    this.authType = loginType
  }

  private submit () {
    this.updateLoginOption(this.authType)
    this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`)
  }

  private goToAccountSettings () {
    this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/login-option`)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.view-container {
  max-width: 60rem;
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
