
import IntelligenceHUD from "./components/IntelligenceHUD";

export default function Home() {
  return (
    <main className="w-screen h-screen flex flex-col justify-end pb-10 pointer-events-none">
      {/* 
        pointer-events-none on the container allows clicking THROUGH the empty space 
        to the real desktop apps below. The HUD component has pointer-events-auto 
        to allow interaction with the overlay itself.
      */}
      <IntelligenceHUD />
    </main>
  );
}
