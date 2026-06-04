import AddFinkPhot from "./AddFinkPhot";

interface SourcePluginsProps {
  source: { id: string };
}

const SourcePlugins = ({ source }: SourcePluginsProps) => (
  <div>
    <AddFinkPhot id={source.id} />
  </div>
);

export default SourcePlugins;
