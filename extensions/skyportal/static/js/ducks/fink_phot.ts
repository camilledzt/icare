import * as API from "../API";

const POST_FINK_PHOTOMETRY = "skyportal/POST_FINK_PHOTOMETRY";

export default function postFinkPhot(id: string, current_magsys?: string) {
  return API.POST(`/api/sources/${id}/fink`, POST_FINK_PHOTOMETRY, {
    magsys: current_magsys || "ab",
  });
}
