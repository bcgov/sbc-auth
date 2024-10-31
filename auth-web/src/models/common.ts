import { ComputedRef } from '@vue/composition-api'

/** Interface for the LaunchTileConfig object */
export interface LaunchTileConfigIF {
  showTile: ComputedRef<boolean>
  image: string
  title: string
  description: string
  href?: string
  action?: () => void
  actionLabel: string
}
