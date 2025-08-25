import { Box } from '@mui/material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import WidgetCard from './WidgetCard';
import { useWidgetLayout } from '../../hooks/useWidgetLayout';

export default function WidgetGrid() {
  const { layout, setLayout } = useWidgetLayout();

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;
    const reordered = Array.from(layout);
    const [moved] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, moved);
    setLayout(reordered);
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="widget-grid" direction="horizontal">
        {(provided) => (
          <Box display="flex" gap={2} ref={provided.innerRef} {...provided.droppableProps}>
            {layout.map((widget, index) => (
              <Draggable key={widget.id} draggableId={widget.id} index={index}>
                {(provided) => (
                  <Box ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps}>
                    <WidgetCard widget={widget} />
                  </Box>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </Box>
        )}
      </Droppable>
    </DragDropContext>
  );
}
