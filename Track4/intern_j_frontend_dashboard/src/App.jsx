import Dashboard from "./components/Dashboard";
import { sampleScript } from "./mock/sampleScript";

// TODO(Intern J): replace sampleScript with a fetch to
// GET /api/results/{task_id} once a real task_id is available (returned
// by POST /api/upload, see api/client.js#uploadScript). Poll
// GET /api/tasks/{task_id} until state is DONE/NEEDS_REVIEW, then load
// the result -- this file currently renders the mock so layout/interaction
// work doesn't block on a live pipeline.
export default function App() {
  return <Dashboard script={sampleScript} />;
}
