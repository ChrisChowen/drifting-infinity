import { createBrowserRouter } from "react-router-dom";

// Layouts
import { HubLayout } from "@components/layout/HubLayout";
import { RunLayout } from "@components/layout/RunLayout";
import { FullscreenLayout } from "@components/layout/FullscreenLayout";

// Pages
import { DashboardPage } from "./pages/DashboardPage";
import { WelcomePage } from "./pages/WelcomePage";
import { CampaignCreateWizard } from "./pages/CampaignCreateWizard";
import { CharacterWizard } from "./pages/CharacterWizard";
import { RunSetupPage } from "./pages/RunSetupPage";
import { ModulePage } from "./pages/ModulePage";
import { PostArenaSummaryPage } from "./pages/PostArenaSummaryPage";
import { RewardSelectionPage } from "./pages/RewardSelectionPage";
import { ShopPage } from "./pages/ShopPage";
import { FloorTransitionPage } from "./pages/FloorTransitionPage";
import { RunCompletePage } from "./pages/RunCompletePage";
import { ArchivePage } from "./pages/ArchivePage";
import { EnhancementForgePage } from "./pages/EnhancementForgePage";
import { GachaPage } from "./pages/GachaPage";
import { PartyManagementPage } from "./pages/PartyManagementPage";
import { CampaignSettingsPage } from "./pages/CampaignSettingsPage";
import { AttunementPage } from "./pages/AttunementPage";
import { ChroniclesPage } from "./pages/ChroniclesPage";
import { FloorPrepPage } from "./pages/FloorPrepPage";
import { ArenaPrepPage } from "./pages/ArenaPrepPage";

export const router = createBrowserRouter([
  // ── Fullscreen (no navigation chrome) ───────────────────────
  {
    element: <FullscreenLayout />,
    children: [
      { path: "/welcome", element: <WelcomePage /> },
    ],
  },

  // ── Hub Mode (sidebar + content) ────────────────────────────
  {
    path: "/",
    element: <HubLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "campaign/new", element: <CampaignCreateWizard /> },
      { path: "party", element: <PartyManagementPage /> },
      { path: "party/add", element: <CharacterWizard /> },
      { path: "forge", element: <EnhancementForgePage /> },
      { path: "gacha", element: <GachaPage /> },
      { path: "attunement", element: <AttunementPage /> },
      { path: "chronicles", element: <ChroniclesPage /> },
      { path: "archive", element: <ArchivePage /> },
      { path: "settings", element: <CampaignSettingsPage /> },
    ],
  },

  // ── Session Prep (uses Hub layout) ─────────────────────────
  {
    path: "/prep",
    element: <HubLayout />,
    children: [
      { path: "floor/:floorNumber", element: <FloorPrepPage /> },
      { path: "floor/:floorNumber/arena/:arenaNumber", element: <ArenaPrepPage /> },
    ],
  },

  // ── Run Mode (progress rail + status bar) ───────────────────
  {
    path: "/run",
    element: <RunLayout />,
    children: [
      { path: "setup", element: <RunSetupPage /> },
      { path: "encounter", element: <ModulePage /> },
      { path: "summary", element: <PostArenaSummaryPage /> },
      { path: "rewards", element: <RewardSelectionPage /> },
      { path: "shop", element: <ShopPage /> },
      { path: "floor-transition", element: <FloorTransitionPage /> },
      { path: "complete", element: <RunCompletePage /> },
    ],
  },
]);
