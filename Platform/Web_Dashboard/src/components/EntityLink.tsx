import React from 'react';
import { useNavigate } from 'react-router-dom';

type EntityKind = 'strategy' | 'ml-model' | 'dataset' | 'group';

interface EntityLinkProps {
  kind: EntityKind;
  governanceId: string;       // pass _governance_id
  children: React.ReactNode;  // display name
  className?: string;
  version?: number;          // pass _version, default to 1
}

function basePath(kind: EntityKind, id?: string, version?: number): string {
  switch (kind) {
    case 'strategy': return `/master-data/strategies/${id}?mode=view&version=${version || 1}`;
    case 'ml-model': return `/master-data/mlmodels/${id}?mode=view&version=${version || 1}`;
    case 'dataset':  return `/master-data/datasets/${id}?mode=view&version=${version || 1}`;
    case 'group':    return `/master-data/groups/${id}?mode=view&version=${version || 1}`;
    default:
        console.error('Unknown kind: ', kind);
        return '/';
  }
}

export const EntityLink: React.FC<EntityLinkProps> = ({ kind, governanceId, children, className, version }) => {
  const navigate = useNavigate();
  const onClick = (e: React.MouseEvent) => {
    e.preventDefault();
    navigate(basePath(kind, governanceId, version), {
      state: { preselectId: governanceId, openView: true, entityKind: kind },
      replace: false,
    });
  };

  return (
    <a href={basePath(kind)} onClick={onClick} className={className}>
      {children}
    </a>
  );
};
