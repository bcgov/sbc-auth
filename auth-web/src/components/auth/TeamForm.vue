<template>
  <div>
    <div v-if="organizations.length > 0">
      You already belong to a team: <span class="font-weight-bold">{{ organizations[0].name }}</span>
      <v-row>
        <v-col cols="12" class="form__btns pb-0">
          <v-btn large color="primary" @click="redirectToNext">OK</v-btn>
        </v-col>
      </v-row>
    </div>
    <div>
      <v-form v-if="organizations.length === 0" ref="createTeamForm">
        <v-radio-group class="mt-0 mb-5 pt-0" v-model="teamType" :mandatory="true">
          <v-radio class="mb-3" label="I manage my own business" value="BASIC"/>
          <v-radio label="I manage multiple businesses on behalf of my clients" value="PREMIUM"/>
        </v-radio-group>
        <v-text-field filled :rules="teamNameRules" v-model.trim="teamName"
                      :label="teamType === 'BASIC' ? 'Your Business Name' : 'Your Management Company or Law Firm Name'"/>
        <v-alert v-show="orgCreateMessage !== 'success'" class="mb-0"
                 dense
                 outlined
                 type="error"
        >{{orgCreateMessage}}
        </v-alert>
        <v-row>
          <v-col cols="12" class="form__btns pb-0">
            <v-btn large color="primary" class="mr-2" :disabled='!isFormValid()' @click="save">
              Save and Continue
            </v-btn>
            <v-btn large color="default" @click="cancel">
              Cancel
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['organizations', 'orgCreateMessage'])
  },
  methods: {
    ...mapActions('org', ['createOrg']),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class TeamForm extends Vue {
    private orgStore = getModule(OrgModule, this.$store)
    private teamName: string = ''
    private teamType: string = 'BASIC'
    private readonly organizations!: Organization[]
    private readonly createOrg!: (requestBody: CreateRequestBody) => Organization
    private readonly syncOrganizations!: () => Organization[]
    private readonly orgCreateMessage: string

    $refs: {
      createTeamForm: HTMLFormElement
    }

    private readonly teamNameRules = [
      v => !!v || 'You must provide a team name'
    ]

    private async mounted () {
      if (!this.organizations) {
        await this.syncOrganizations()
      }
    }

    private isFormValid (): boolean {
      return !!this.teamName
    }

    private async save () {
      // Validate form, and then create an team with this user a member
      if (this.isFormValid()) {
        const createRequestBody: CreateRequestBody = {
          name: this.teamName,
          typeCode: this.teamType === 'BASIC' ? 'IMPLICIT' : 'EXPLICIT'
        }
        await this.createOrg(createRequestBody)
        if (this.orgCreateMessage === 'success') {
          this.redirectToNext()
        }
      }
    }

    private cancel () {
      this.$router.push({ path: '/home' })
    }

    private redirectToNext () {
      this.$router.push({ path: '/main' })
    }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }
</style>
