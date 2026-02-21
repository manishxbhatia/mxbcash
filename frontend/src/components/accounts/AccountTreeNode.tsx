import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { AccountTreeNode as TreeNode, Commodity } from "../../types";
import { formatCents } from "../../utils/money";

interface Props {
  node: TreeNode;
  commodities: Commodity[];
  balances: Record<number, number>;
  depth?: number;
  onEdit: (node: TreeNode) => void;
  onDelete: (id: number) => void;
}

export default function AccountTreeNodeComp({ node, commodities, balances, depth = 0, onEdit, onDelete }: Props) {
  const [expanded, setExpanded] = useState(depth < 2);
  const navigate = useNavigate();

  const commodity = commodities.find((c) => c.id === node.commodity_id);
  const balance = balances[node.id] ?? 0;
  const hasChildren = node.children.length > 0;

  function handleRowClick() {
    if (!node.placeholder) {
      navigate(`/accounts/${node.id}/register`);
    } else {
      setExpanded(!expanded);
    }
  }

  return (
    <div className="tree-node">
      <div className="tree-row" onClick={handleRowClick}>
        <span className="tree-toggle">
          {hasChildren ? (expanded ? "▾" : "▸") : ""}
        </span>
        <span className="tree-name" style={{ fontWeight: node.placeholder ? 600 : 400 }}>
          {node.name}
          {node.placeholder && <span style={{ color: "var(--muted)", fontSize: "11px", marginLeft: "4px" }}>(placeholder)</span>}
        </span>
        <span className="tree-balance">
          {commodity ? formatCents(balance, commodity.fraction) : balance} {commodity?.mnemonic}
        </span>
        <span className="tree-actions">
          <button
            className="btn btn-ghost"
            style={{ padding: "0.15rem 0.4rem", fontSize: "11px" }}
            onClick={(e) => { e.stopPropagation(); onEdit(node); }}
          >Edit</button>
          <button
            className="btn btn-danger"
            style={{ padding: "0.15rem 0.4rem", fontSize: "11px" }}
            onClick={(e) => { e.stopPropagation(); onDelete(node.id); }}
          >Del</button>
        </span>
      </div>
      {hasChildren && expanded && (
        <div className="tree-children">
          {node.children.map((child) => (
            <AccountTreeNodeComp
              key={child.id}
              node={child}
              commodities={commodities}
              balances={balances}
              depth={depth + 1}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
